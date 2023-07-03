#   Copyright (C) 2021 - 2023 52°North Spatial Information Research GmbH
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# If the program is linked with libraries which are licensed under one of
# the following licenses, the combination of the program with the linked
# library is not considered a "derivative work" of the program:
#
#     - Apache License, version 2.0
#     - Apache Software License, version 1.0
#     - GNU Lesser General Public License, version 3
#     - Mozilla Public License, versions 1.0, 1.1 and 2.0
#     - Common Development and Distribution License (CDDL), version 1.0
#
# Therefore the distribution of the program linked with libraries licensed
# under the aforementioned licenses, is permitted by the copyright holders
# if the distribution is compliant with both the GNU General Public
# License version 2 and the aforementioned licenses.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
import datetime

import pytest
import xarray

import utils.graphics as graphics
from constraints.constraints import *
from ship.shipparams import ShipParams
from weather import *

def test_plot_power_vs_dist():
    count = 3
    dummy_scalar = 0
    dummy_list = np.array([])
    fuel_consumed = np.array([1,2,1])
    dist_per_step = np.array([1,4,5])


    sp = ShipParams(fuel_consumed, dummy_list, dummy_list,dummy_list)

    route = RouteParams(
        count = count,  # routing step
        start = dummy_list,  # lat, lon at start
        finish = dummy_list,  # lat, lon at end
        #fuel = dummy_scalar,  # sum of fuel consumption [kWh]
        #rpm = dummy_scalar,  # propeller [revolutions per minute]
        route_type = 'min_time_route',  # route name
        time = dummy_scalar,  # time needed for the route [h]
        lats_per_step=dummy_list,
        lons_per_step=dummy_list,
        azimuths_per_step= dummy_list,
        dists_per_step = dist_per_step,
        #speed_per_step = dummy_list,
        starttime_per_step = dummy_list,
        #fuel_per_step= fuel_consumed,
        #full_dist_traveled = dummy_list,
        ship_params_per_step=sp,
        gcr = dummy_list
    )
    route.plot_power_vs_dist("orange", "Route X")

def test_get_accumulated_dist():
    dist_per_step = np.array([1,4,5,7])
    dist_acc_test = np.array([1,5,10,17])
    dist = graphics.get_accumulated_dist(dist_per_step)

    assert np.array_equal(dist_acc_test, dist)

def test_get_hist_values_from_boundaries():
    bin_boundaries = np.array([1,4,5,7])
    bin_content_unnormalised = np.array([1,3,5])
    bin_content_normalised_test = np.array([1/3, 3, 5/2])
    bin_centres_test = np.array([2.5, 4.5, 6])
    bin_widths_test  = np.array([3, 1, 2])

    hist_values = graphics.get_hist_values_from_boundaries(bin_boundaries, bin_content_unnormalised)

    assert np.array_equal(bin_centres_test, hist_values['bin_centres'])
    assert np.array_equal(bin_widths_test, hist_values['bin_widths'])
    assert np.array_equal(bin_content_normalised_test, hist_values['bin_content'])

def test_get_hist_values_from_widths():
    bin_widths = np.array([3,1,2])
    bin_content_unnormalised = np.array([1,3,5])
    bin_content_normalised_test = np.array([1/3, 3, 5/2])
    bin_centres_test = np.array([1.5, 3.5, 5])

    hist_values = graphics.get_hist_values_from_widths(bin_widths, bin_content_unnormalised)

    assert np.array_equal(bin_centres_test, hist_values['bin_centres'])
    assert np.array_equal(bin_content_normalised_test, hist_values['bin_content'])
