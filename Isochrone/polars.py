"""
Boat polars file
Have TWA(True wind Angle) and TWS (True Wind speed) value for calculate boat speed and properties


"""
import numpy as np
import math
import matplotlib.pyplot as plt
import netCDF4 as nc
from scipy.interpolate import RegularGridInterpolator
import xarray as xr

import utils as ut
import mariPower
from mariPower import ship
from mariPower import __main__
from utils import knots_to_mps  # Convert  knot value in meter per second
from weather import WeatherCond

class Boat:
    speed: float
    simple_fuel_model: xr.Dataset

    def __init__(self):
        self.speed = -99

    def get_rpm(self):
        pass

    def get_fuel_per_time(self):
        pass


class Tanker(Boat):
    rpm: int
    hydro_model: mariPower.ship

    def __init__(self, rpm):
        Boat.__init__(self)
        self.rpm = rpm

    def init_hydro_model_single_pars(self):
        debug = True
        self.hydro_model = mariPower.ship.CBT()
        #shipSpeed = 13 * 1852 / 3600
        self.hydro_model.WindDirection = math.radians(90)
        self.hydro_model.WindSpeed = 0
        self.hydro_model.TemperatureWater = 10

        self.hydro_model.WaveSignificantHeight = 2
        self.hydro_model.WavePeakPeriod = 10.0
        self.hydro_model.WaveDirection = math.radians(45)

        self.hydro_model.CurrentDirection = math.radians(0)
        self.hydro_model.CurrentSpeed = 0.5

        self.MaxIterations = 5

        print('Setting environmental parameters of tanker:')
        print('     water temp', self.hydro_model.TemperatureWater)
        print('     wave significant height', self.hydro_model.WaveSignificantHeight)
        print('     wave peak period', self.hydro_model.WavePeakPeriod)
        print('     wave dir', self.hydro_model.WaveDirection)
        print('     current dir', self.hydro_model.CurrentDirection)
        print('     current speed', self.hydro_model.CurrentSpeed)

    def init_hydro_model_NetCDF(self, netCDF_filepath):
        self.hydro_model = mariPower.ship.CBT()
        Fx, driftAngle, ptemp, n, delta = mariPower.__main__.PredictPowerForNetCDF(self.hydro_model, netCDF_filepath)

    def init_hydro_model_Route(self, netCDF_filepath):
        self.hydro_model = mariPower.ship.CBT()
        Fx, driftAngle, ptemp, n, delta = mariPower.__main__.PredictPowerRoute(self.hydro_model, netCDF_filepath)

    def set_boat_speed(self, speed):
        self.speed = speed

    def set_rpm(self, rpm):
        self.rpm = rpm
    def get_rpm(self):
        return self.rpm

    def get_fuel_per_course_simple(self, course, wind_speed, wind_dir):
        debug = False
        angle = np.abs(course-wind_dir)
        if angle>180: angle = np.abs(360 - angle)
        if debug:
            ut.print_line()
            ut.print_step('course = ' + str(course),1)
            ut.print_step('wind_speed = ' + str(wind_speed), 1)
            ut.print_step('wind_dir = ' + str(wind_dir), 1)
            ut.print_step('delta angle = ' + str(angle), 1)
        wind_speed = wind_speed
        power = self.simple_fuel_model.interp(delta_angle=angle, wind_speed=wind_speed)['power'].to_numpy()

        if debug: ut.print_step('power = ' + str(power), 1)
        return power

    #def get_fuel_per_time_simple(self, delta_time):
    #    f = 0.0007 * self.rpm ** 3 + 0.0297 * self.rpm ** 2 + 2.8414 * self.rpm - 19.359  # fuel [kg/h]
    #    f *= delta_time / 3600 * 1 / 1000  # amount of fuel for this time interval
    #    return f

    def get_fuel_per_course(self, course, wind_dir, wind_speed, boat_speed):
        #boat_speed = np.array([boat_speed])
        self.hydro_model.WindDirection = math.radians(wind_dir)
        self.hydro_model.WindSpeed = wind_speed
        ut.print_step('course [degrees]= ' + str(course), 1)
        course = ut.degree_to_pmpi(course)
        ut.print_step('course [rad]= ' + str(course), 1)
        ut.print_step('wind dir = ' + str(self.hydro_model.WindDirection), 1)
        ut.print_step('wind speed = ' + str(self.hydro_model.WindSpeed), 1)
        ut.print_step('boat_speed = ' + str(boat_speed),1)
        #Fx, driftAngle, ptemp, n, delta = self.hydro_model.IterateMotionSerial(course, boat_speed, aUseHeading=True,
        #                                                                 aUpdateCalmwaterResistanceEveryIteration=False)
        Fx, driftAngle, ptemp, n, delta = self.hydro_model.IterateMotion(course, boat_speed, aUseHeading=True,
                                                                               aUpdateCalmwaterResistanceEveryIteration=False)

        return ptemp

    def calibrate_simple_fuel(self):
        self.simple_fuel_model = xr.open_dataset("/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/SimpleFuelModel/simple_fuel_model.nc")
        ut.print_line()
        print('Initialising simple fuel model')
        print(self.simple_fuel_model)

    def write_simple_fuel(self):
        n_angle = 10
        n_wind_speed = 20
        power = np.zeros((n_angle, n_wind_speed))
        delta_angle = ut.get_bin_centers(0,180,n_angle)
        wind_speed = ut.get_bin_centers(0,60,n_wind_speed)

        coords = dict(
            delta_angle=(["delta_angle"], delta_angle),
            wind_speed=(["wind_speed"], wind_speed),
        )
        attrs = dict(description="Necessary descriptions added here.")

        for iang in range(0,n_angle):
            for iwind_speed in range(0,n_wind_speed):
                course = 0
                wind_dir = 0 + delta_angle[iang]
                power[iang,iwind_speed]= self.get_fuel_per_course(course, wind_dir, wind_speed[iwind_speed], self.speed)

        data_vars = dict(
            power=(["delta_angle", "wind_speed"], power),
        )

        ds = xr.Dataset(data_vars, coords, attrs)
        ds.to_netcdf('/home/kdemmich/MariData/Code/simple_fuel_model.nc')

        print('Writing simple fuel model:')
        print(ds)
        raise Exception('Stop here')

    def get_fuel_per_time(self, courses, wind):
        debug = False

        if(debug):
            print('Requesting power calculation')
            course_str = 'Courses:' + str(courses)
            ut.print_step(course_str,1)

        P = np.zeros(courses.shape)
        for icours in range(0,courses.shape[0]):
            #P[icours] = self.get_fuel_per_course(courses[icours], wind['twa'][icours], wind['tws'][icours], self.speed)
            P[icours] = self.get_fuel_per_course_simple(courses[icours], wind['tws'][icours],  wind['twa'][icours])
            if math.isnan(P[icours]): P[icours] = 1000000000000000

        if(debug):
            ut.print_step('power consumption' + str(P))
        return P

    def get_fuel_per_time_netCDF(self, courses, lats, lons, time):
        debug = True

        if (debug):
            print('Requesting power calculation')
            time_str = 'Time:' + str(time)
            lats_str = 'Latitude:' + str(lats)
            lons_str = 'Longitude:' + str(lons)
            course_str = 'Courses:' + str(courses)
            speed_str = 'Boat speed:' + str(self.speed)
            ut.print_step(time_str, 1)
            ut.print_step(lats_str, 1)
            ut.print_step(lons_str, 1)
            ut.print_step(course_str, 1)
            ut.print_step(speed_str, 1)

        raise Exception('Stop here')

        #data_vars = dict(
        #    courses=(["time", "latitude", "longitude"], courses),
        #    boat_speed=(["time", "latitude", "longitude"], self.speed),
        #)

        #coords = dict(
        #    latitude=(["latitude"], lat),
        #    longitude=(["longitude"], lon),
        #    time=(["time"], t),
        #)



    def boat_speed_function(self, wind):
        speed = np.array([self.speed])
        speed = np.repeat(speed, wind['twa'].shape, axis=0)
        return speed

    def test_power_consumption_per_course(self):
        courses = np.linspace(0, 360, num=21, endpoint=True)
        wind_dir = 45
        wind_speed = 2
        power = np.zeros(courses.shape)

        #get_fuel_per_course gets angles in degrees from 0 to 360
        for i in range(0,courses.shape[0]):
            power[i] = self.get_fuel_per_course(courses[i], wind_dir, wind_speed, self.speed)
            #power[i] = self.get_fuel_per_time_simple(i*3600)

        #plotting with matplotlib needs angles in radiants
        fig, axes = plt.subplots(1,2,subplot_kw={'projection': 'polar'})
        for i in range(0,courses.shape[0]): courses[i] = math.radians(courses[i])
        wind_dir = math.radians(wind_dir)

        axes[0].plot(courses, power)
        axes[0].legend()
        for ax in axes.flatten():
            ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
            ax.set_theta_zero_location("S")
            ax.grid(True)
        axes[1].plot([wind_dir, wind_dir], [0,wind_speed], color='blue', label='Wind')
        #axes[1].plot([self.hydro_model.WaveDirection, self.hydro_model.WaveDirection], [0, 1 * (self.hydro_model.WaveSignificantHeight > 0.0)],
        #                color='green', label='Seaway')
        #axes[1].plot([self.hydro_model.CurrentDirection, self.hydro_model.CurrentDirection], [0, 1 * (self.hydro_model.CurrentSpeed > 0.0)],
        #                color='purple', label='Current')
        axes[1].legend()

        axes[0].set_title("Power", va='bottom')
        axes[1].set_title("Environmental conditions", va='top')
        plt.show()

    def test_power_consumption_per_speed(self):
        course = 10
        boat_speed = np.linspace(1,20, num=17)
        wind_dir = 45
        wind_speed = 2
        power = np.zeros(boat_speed.shape)

        for i in range(0,boat_speed.shape[0]):
            power[i] = self.get_fuel_per_course(course, wind_dir, wind_speed, boat_speed[i])
            #power[i] = self.get_fuel_per_time_simple(i*3600)

        plt.plot(boat_speed, power, 'r--')
        plt.xlabel('speed (m/s)')
        plt.ylabel('power (W)')
        plt.show()

class SailingBoat(Boat):
    polars: np.ndarray
    speedfunction: float

    def __init__(self, filepath):
        Boat.__init__(self)
        self.set_speed_function(filepath)

    def set_speed_function(self, filepath):
        """
        Load boat properties from boat file.

            Parameters:
                    filepath (string): Path to polars file polar VO7O

            Returns:
                    boat (dict): Dict with function and raw polars
        """
        self.polars = np.genfromtxt(filepath, delimiter=';')
        self.polars = np.nan_to_num(self.polars)  # Replace with NAN value with the zero or infinity values

        ws = self.polars[0, 1:]
        wa = self.polars[1:, 0]
        values = self.polars[1:, 1:]

        # internally we use only meters per second
        ws = knots_to_mps(ws)
        values = knots_to_mps(values)

        self.speedfunc = RegularGridInterpolator(  # returns interpolated grid
            (ws, wa), values.T,
            bounds_error=False,
            fill_value=None
        )
        # return {'func': f, 'polars': polars}

    def boat_speed_function(self, wind):
        """
        Vectorized boat speed function.

            Parameters:
                    boat (dict): Boat dict with wind function
                    wind (dict): Wind dict with TWA and TWS arrays

            Returns:
                    boat_speed (array): Array of boat speeds
        """
        twa = wind['twa']
        tws = wind['tws']

        # Assert to check the condition if false give assertion error
        assert twa.shape == tws.shape, "Input shape mismatch"
        # func = boat['func']

        # get rid of negative and above 180
        twa = np.abs(twa)
        twa[twa > 180] = 360. - twa[twa > 180]

        # init boat speed vector
        boat_speed = self.speedfunc((tws, twa))
        return boat_speed

    def get_speed_dict(self):
        return {'func': self.speedfunc, 'polars': self.polars}

    def get_rpm(self):
        return 0

    def get_fuel_per_time(self, course, wt : WeatherCond):
        fuel = np.zeros(course.shape)
        return fuel
