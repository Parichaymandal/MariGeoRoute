import datetime as dt
import logging
import warnings
import logging.handlers

import WeatherRoutingTool.config as config
import WeatherRoutingTool.utils.graphics as graphics
from WeatherRoutingTool.ship.ship import Tanker
from WeatherRoutingTool.weather_factory import WeatherFactory
from WeatherRoutingTool.constraints.constraints import *
from WeatherRoutingTool.algorithms.routingalg_factory import *
from WeatherRoutingTool.utils.maps import Map


def merge_figures_to_gif(path, nof_figures):
    graphics.merge_figs(path, nof_figures)


if __name__ == "__main__":
    ##
    # initialise logging
    logger = logging.getLogger('WRT')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(config.PERFORMANCE_LOG_FILE, mode='w')
    fh.setLevel(logging.WARNING)
    fhinfo = logging.FileHandler(config.INFO_LOG_FILE, mode='w')
    fhinfo.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    fh.setFormatter(formatter)
    fhinfo.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(fhinfo)

    ##
    # suppress warnings from mariPower
    # warnings.filterwarnings("ignore")

    # *******************************************
    # basic settings
    windfile = config.WEATHER_DATA
    depthfile = config.DEPTH_DATA
    coursesfile = config.COURSES_FILE
    figurepath = config.FIGURE_PATH
    routepath = config.ROUTE_PATH
    time_resolution = config.DELTA_TIME_FORECAST
    time_forecast = config.TIME_FORECAST
    lat1, lon1, lat2, lon2 = config.DEFAULT_MAP
    departure_time = dt.datetime.strptime(config.DEPARTURE_TIME, '%Y-%m-%dT%H:%MZ')
    default_map = Map(lat1, lon1, lat2, lon2)

    # *******************************************
    # initialise weather
    #
    # wt = WeatherCondEnvAutomatic(departure_time, time_forecast, 3)
    # wt.set_map_size(default_map)
    # wt.read_dataset()
    # weather_path = wt.write_data('/home/kdemmich/MariData/Code/Data/WheatherFiles')

    # wt_read = WeatherCondFromFile(departure_time, time_forecast, 3)
    # wt_read.read_dataset(weather_path)
    # wt.write_data('/home/kdemmich/MariData/Code/Data/WheatherFiles')
    wf = WeatherFactory()
    wt = wf.get_weather(config.DATA_MODE, windfile, departure_time, time_forecast, time_resolution, default_map)

    # *******************************************
    # initialise boat
    boat = Tanker(-99)
    boat.init_hydro_model_Route(windfile, coursesfile, depthfile)
    boat.set_boat_speed(config.BOAT_SPEED)

    # *******************************************
    # initialise constraints
    '''pars = ConstraintPars()
    land_crossing = LandCrossing()
    # seamarks_crossing = SeamarkCrossing()
    # water_depth.plot_depth_map_from_file(depthfile, lat1, lon1, lat2, lon2)
    on_map = StayOnMap()
    on_map.set_map(lat1, lon1, lat2, lon2)
    continuous_checks_seamarks = SeamarkCrossing()
    continuous_checks_land = LandPolygonsCrossing()

    constraint_list = ConstraintsList(pars)
    constraint_list.add_neg_constraint(land_crossing)
    constraint_list.add_neg_constraint(on_map)
    constraint_list.add_neg_constraint(water_depth)
    # constraint_list.add_neg_constraint(continuous_checks_seamarks,
    # 'continuous')
    # constraint_list.add_neg_constraint(continuous_checks_land, 'continuous')
    constraint_list.print_settings()'''

    water_depth = WaterDepth(config.DATA_MODE, config.BOAT_DRAUGHT, default_map, depthfile)
    constraint_list = ConstraintsListFactory.get_constraints_list(
        ['land_crossing_global_land_mask', 'water_depth', 'on_map'], config.DATA_MODE, config.BOAT_DRAUGHT, default_map,
        depthfile)

    # *******************************************
    # initialise route
    min_fuel_route = RoutingAlgFactory.get_routing_alg('isofuel')
    min_fuel_route.init_fig(water_depth, default_map)

    # *******************************************
    # routing
    min_fuel_route = min_fuel_route.execute_routing(boat, wt, constraint_list)
    # min_fuel_route.print_route()
    # min_fuel_route.write_to_file(str(min_fuel_route.route_type) +
    # "route.json")
    min_fuel_route.return_route_to_API(routepath + '/' + str(min_fuel_route.route_type) + ".json")
