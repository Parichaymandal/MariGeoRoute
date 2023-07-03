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
import pygrib as pg
filepath='wind-router-master/wind-router-master/data/2019122212/20205150000_split13.grb'
import pandas as np

#import pygrib as pg# Provides a high-level interface to  ECCODES C library for reading GRIB files

"""GRIB is a file format for the storage and transport of gridded meteorological data,"""
#grib_data = cfgrib.open_datasets(filepath)

#print('print cf grib',grib_data)
grib=pg.open(filepath)
for g in grib:
    lt,ln=g.latlons()
    lt,ln=np.array(lt),np.array(ln)
    print('lt and ln',lt,ln)
#u, _, _ = grib_data[1].data()  # U for Initial
#print(u)
#grbs = pg.open(filepath)
#print(grbs)
#u, _, _ = grbs[1].data()
#print(u)


grbs = pg.open(filepath)
u, _, _ = grbs[1].data() # U for Initial


print(u)
#grbs.seek(0)
#for grb in grbs:
 #   print('grbs',grb)

#a=grbs.select(name='U')
#print('printing a',a)


print('hello')
print('hello')

#v, _, _ = grbs[2].data() # V for Final
lat1, lon1, lat2, lon2= [30, 0, 45, 40]
u, lats_u, lons_u = grbs[1].data(lat1, lat2, lon1, lon2)
v, lats_v, lons_v = grbs[2].data(lat1, lat2, lon1, lon2)

print(u)
print('lat_u',lats_u)
print('lon_u',lons_u)
print('u',u)


"""
print(u)
#print(v[0])
tws = np.sqrt(u * u + v * v)
twa = 180.0 / np.pi * np.arctan2(u, v) + 180.0#arctan:This mathematical function helps user to calculate inverse tangent for all x(being the array elements

#print(tws)
#print(twa)
lats_grid = np.linspace(-90, 90, 181)#Linespace : is a tool in Python for creating numeric sequences.
lons_grid = np.linspace(0, 360, 361)

print(lats_grid)
print(lons_grid)

f_twa = RegularGridInterpolator((lats_grid, lons_grid),np.flip(np.hstack((twa, twa[:, 0].reshape(181, 1))), axis=0),)#hstack() function is used to stack the sequence of input arrays horizontally (i.e. column wise) to make a single array

f_tws = RegularGridInterpolator(
        (lats_grid, lons_grid),
        np.flip(np.hstack((tws, tws[:, 0].reshape(181, 1))), axis=0),
    )
#print(f_tws)
#print(f_twa)

"""

#rows = 41
#b = 35
#for i in range(rows, 0, -1):
 #   b += 1
  #  a=[]
   # for j in range(lat1, lat2):
    #    print(b, end=' ')
     #   a.append(b)

    #print('\r')
# reverse for loop from 5 to 0

