import numpy as np
import datetime as dt
from typing import NamedTuple
import json
import dateutil.parser

import utils
import matplotlib.pyplot as plt
import graphics
from utils import NumpyArrayEncoder
from shipparams import ShipParams


class RouteParams():
    """
        Isochrone data structure with typing.
                Parameters:
                    count: int  (routing step)
                    start: tuple    (lat,long at start)
                    finish: tuple   (lat,lon and end)
                    gcr_azi: float (initial gcr heading)
                    lats1, lons1, azi1, s12: (M, N) arrays, N=headings+1, M=number of steps+1 (decreasing step number)
                    azi0, s0: (M, 1) vectors without history
                    time1: current datetime
                    elapsed: complete elapsed timedelta
        """
    count: int  # routing step
    start: tuple  # lat, lon at start
    finish: tuple  # lat, lon at end
    #fuel: float
    #full_dist_traveled: tuple
    gcr: tuple
    route_type: str  # route name
    time: dt.timedelta  # time needed for the route [datetime]

    ship_params_per_step: ShipParams
    #fuel_per_step: tuple  # sum of power consumption [W]
    #rpm_per_step: tuple
    #power_per_step: tuple
    #speed_per_step: tuple  # boat speed per step [m/s]

    lats_per_step: tuple  # lats: (M,N) array, N=headings+1, M=steps (M decreasing)
    lons_per_step: tuple  # longs: (M,N) array, N=headings+1, M=steps
    azimuths_per_step: tuple  # azimuth: (M,N) array, N=headings+1, M=steps [degree]
    dists_per_step: tuple  # geodesic distance traveled per time stamp: (M,N) array, N=headings+1, M=steps [m]
    starttime_per_step: tuple
    full_dist_traveled: tuple  # full geodesic distance since start [m]

    def __init__(self, count, start, finish, fuel, full_dist_traveled,gcr, rpm, route_type, time, lats_per_step, lons_per_step, azimuths_per_step, dists_per_step, speed_per_step, starttime_per_step, fuel_per_step, power_per_step, rpm_per_step):
        self.count = count  # routing step
        self.start = start  # lat, lon at start
        self.finish = finish  # lat, lon at end
        self.fuel = fuel  # sum of fuel consumption [kWh]
        self.full_dist_traveled = full_dist_traveled #full travel distance [m]
        self.gcr = gcr
        self.rpm = rpm  # propeller [revolutions per minute]
        self.route_type = route_type  # route name
        self.time = time  # time needed for the route [h]
        self.lats_per_step = lats_per_step
        self.lons_per_step = lons_per_step
        self.azimuths_per_step = azimuths_per_step # [degrees]
        self.dists_per_step = dists_per_step    #travel distance per step [m]
        self.speed_per_step = speed_per_step    #speed per step [m/s]
        self.starttime_per_step =starttime_per_step	# time at start of every step
        self.fuel_per_step = fuel_per_step 	#fuel consumption per step [kWh]
        self.power_per_step = power_per_step  # fuel consumption per step [kWh]
        self.rpm_per_step = rpm_per_step  # fuel consumption per step [kWh]

    def print_route(self):
        utils.print_line()
        print('Printing route:  ' + str(self.route_type))
        print('Going from', self.start)
        print('to')
        print(self.finish)
        print('routing steps ' + str(self.count))
        print('time ' + str(self.time))
        print('fuel ' + str(self.fuel/1000))
        print('full_dist_traveled ' + str(self.full_dist_traveled))
        print('gcr ' + str(self.gcr))
        print('rpm ' + str(self.rpm))
        print('lats_per_step ' + str(self.lats_per_step))
        print('lons_per_step ' + str(self.lons_per_step))
        print('azimuths_per_step ' + str(self.azimuths_per_step))
        print('dists_per_step ' + str(self.dists_per_step))
        print('speed_per_step ' + str(self.speed_per_step))
        print('start_time_per_step' + str(self.starttime_per_step))
        print('fuel_per_step' + str(self.fuel_per_step/1000))
        print('power_per_step' + str(self.power_per_step/1000))
        print('rpm_per_step' + str(self.rpm_per_step))

        utils.print_line()

    def __eq__(self, route2):
        bool_equal=True
        if not (self.count == route2.count):
            raise ValueError('Route counts not matching')
        if not (np.array_equal(self.start, route2.start)):
            raise ValueError('Route start not matching')
        if not (np.array_equal(self.finish, route2.finish)):
            raise ValueError('Route finsh not matching')
        if not (np.array_equal(self.time, route2.time)):
            raise ValueError('Route time not matching: self=' + str(self.time) + ' other=' + str(route2.time))
        if not (np.array_equal(self.fuel, route2.fuel)):
            raise ValueError('Route fuel not matching: self=' + str(self.fuel) + ' other=' + str(route2.fuel))
        if not (np.array_equal(self.rpm, route2.rpm)):
            raise ValueError('Route rpm not matching')
        if not (np.array_equal(self.lats_per_step, route2.lats_per_step)):
            raise ValueError('Route lats_per_step not matching')
        if not (np.array_equal(self.lons_per_step, route2.lons_per_step)):
            raise ValueError('Route lons_per_step not matching')
        if not (np.array_equal(self.azimuths_per_step, route2.azimuths_per_step)):
            raise ValueError('Route azimuths_per_step not matching')
        if not (np.array_equal(self.dists_per_step, route2.dists_per_step)):
            raise ValueError('Route dists_per_step not matching')
        if not (np.array_equal(self.full_dist_traveled, route2.full_dist_traveled)):
            raise ValueError('Route full_dist_traveled not matching')

        return bool_equal

    def convert_to_dict(self):
        rp_dict = {
            "count" : self.count,
            "start" : self.start,
            "finish": self.finish,
            "fuel": self.fuel,
            "full_dist_traveled": self.full_dist_traveled,
            "gcr": self.gcr,
            "rpm" : self.rpm,
            "route type" : self.route_type,
            "time" : self.time,
            "fuel_per_step" : self.fuel_per_step,
            "lats_per_step" : self.lats_per_step,
            "lons_per_step" : self.lons_per_step,
            "azimuths_per_step" : self.azimuths_per_step,
            "dists_per_step" : self.dists_per_step,
            "speed_per_step" : self.speed_per_step,
            "starttime_per_step" : self.starttime_per_step,
        }
        return rp_dict

    def write_to_file(self, filename):
        rp_dict = self.convert_to_dict()
        with open(filename, 'w') as file:
            json.dump(rp_dict, file, cls=NumpyArrayEncoder, indent=4)

    @classmethod
    def from_file(cls, filename):
        with open(filename) as file:
            rp_dict = json.load(file)

        count = rp_dict['count']
        start = rp_dict['start']
        finish = rp_dict['finish']
        fuel = rp_dict['fuel']
        full_dist_traveled = rp_dict['full_dist_traveled']
        gcr = rp_dict['gcr']
        rpm = rp_dict['rpm']
        route_type = rp_dict['route type']
        time = rp_dict['time']
        lats_per_step = np.asarray(rp_dict['lats_per_step'])
        lons_per_step = np.asarray(rp_dict['lons_per_step'])
        azimuths_per_step = np.asarray(rp_dict['azimuths_per_step'])
        dists_per_step = np.asarray(rp_dict['dists_per_step'])
        speed_per_step = np.asarray(rp_dict['speed_per_step'])
        starttime_per_step = np.asarray(rp_dict['starttime_per_step'])
        fuel_per_step = np.asarray(rp_dict['fuel_per_step'])

        return cls(
            count = count,
            start = start,
            finish = finish,
            fuel = fuel,
            full_dist_traveled = full_dist_traveled,
            gcr = gcr,
            rpm = rpm,
            route_type = route_type,
            time = time,
            lats_per_step = lats_per_step,
            lons_per_step = lons_per_step,
            azimuths_per_step = azimuths_per_step,
            dists_per_step = dists_per_step,
            speed_per_step = speed_per_step,
            starttime_per_step = starttime_per_step,
            fuel_per_step = fuel_per_step
        )
    def plot_route(self, ax, colour, label):
        lats = self.lats_per_step
        lons = self.lons_per_step
        ax.plot(lons, lats, color = colour, label = label, linewidth=2)

        ax.plot(self.start[1], self.start[0], marker="o", markerfacecolor=colour, markeredgecolor=colour,
                markersize=10)
        ax.plot(self.finish[1], self.finish[0], marker="o", markerfacecolor=colour, markeredgecolor=colour,
                markersize=10)
        return ax

    def plot_power_vs_dist(self, color, label):
        power = self.fuel_per_step
        dist = self.dists_per_step
        lat = self.lats_per_step
        lon = self.lons_per_step

        dist = dist/1000    # [m] -> [km]
        hist_values = graphics.get_hist_values_from_widths(dist, power)

        plt.bar(hist_values["bin_centres"], hist_values["bin_content"], dist, fill=False, color = color, edgecolor = color, label = label)
        plt.xlabel('Weglänge (km)')
        plt.ylabel('Energie (kWh/km)')
        plt.xticks()
