#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  2 21:52:38 2026

@author: zhouyangtianli
"""

import numpy as np
import pandas as pd
import pyproj
from cartopy import crs as ccrs
import matplotlib.pyplot as plt
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
from tqdm import tqdm
from raypath_utils import cal_raypath


projection = pyproj.Geod(ellps='WGS84')
model_prem = TauPyModel(model="prem")


def cal_pierce(latS, lonS, depS, latR, lonR, phase):
    az_SR, baz_SR, dist_SR_km = projection.inv(lonS, latS, lonR, latR)
    gcarc = locations2degrees(latS, lonS, latR, lonR)
    pierces_prem = model_prem.get_pierce_points(source_depth_in_km=depS,
                                                distance_in_degree=gcarc,
                                                phase_list=[phase])
    if len(pierces_prem) > 0:
        path = pierces_prem[0].pierce
        pierces_points = [list(item) for item in path]
        pcmb = []
        for ppoint in pierces_points:
            if ppoint[3] == 2891:
                pcmb.append(ppoint)

        pcmb_in = pcmb[0]
        pcmb_out = pcmb[-1]
        angle_pcmb_in = 180*pcmb_in[2]/np.pi
        angle_pcmb_out = 180*pcmb_out[2]/np.pi
        dist_in_km = dist_SR_km*angle_pcmb_in/gcarc
        dist_out_km = dist_SR_km*angle_pcmb_out/gcarc

        lonPin, latPin, bazPin = projection.fwd(lonS, latS,
                                                az_SR, dist_in_km)
        lonPout, latPout, bazPout = projection.fwd(lonS, latS,
                                                   az_SR, dist_out_km)
    else:
        latPin = np.nan
        lonPin = np.nan
        latPout = np.nan
        lonPout = np.nan
    return latPin, lonPin, latPout, lonPout


df_traces = pd.read_csv('../Data/df_all_measurements.csv')
df_traces = df_traces[df_traces.group > -1]
df_traces = df_traces.reset_index(drop=True)

'''
raypath_array_lon = np.zeros((500, len(df_traces)))
raypath_array_lat = np.zeros((500, len(df_traces)))

total_traces = len(df_traces)
for idx, row in tqdm(df_traces.iterrows(), total=total_traces):
    latS = row.evla
    lonS = row.evlo
    depS = row.evdp
    latR = row.stla
    lonR = row.stlo
    latPin_s3ks, lonPin_s3ks, latPout_s3ks, lonPout_s3ks = cal_pierce(
        latS, lonS, depS, latR, lonR, phase='SKKKS')
    raypath = cal_raypath(latPin_s3ks, lonPin_s3ks,
                          latPout_s3ks, lonPout_s3ks)
    raypath_array_lon[:, idx] = raypath[:, 0]
    raypath_array_lat[:, idx] = raypath[:, 1]

df_raypath = pd.DataFrame({'longitude': raypath_array_lon.flatten(),
                           'latitude': raypath_array_lat.flatten()})

df_raypath.to_csv('figure1_all_raypath.csv')
'''

# when it's already calcualted
# df_raypath = pd.read_csv('figure1_all_raypath.csv')

lon_list = np.arange(-180, 181, 2)
lat_list = np.arange(-90, 91, 2)
X, Y = np.meshgrid(lon_list, lat_list)
Z = np.zeros((len(lat_list), len(lon_list)))
xx = X.flatten()
yy = Y.flatten()
npts = len(xx)

'''
radius = 2
for i in tqdm(np.arange(npts)):
    xmin = xx[i] - radius
    xmax = xx[i] + radius
    ymin = yy[i] - radius
    ymax = yy[i] + radius
    df_nearby = df_raypath[(df_raypath.longitude > xmin) &
                           (df_raypath.longitude < xmax) &
                           (df_raypath.latitude > ymin) &
                           (df_raypath.latitude < ymax)]
    if len(df_nearby) > 0:
        ix = int(i // 181)
        iy = int(i % 181)
        Z[ix, iy] = 1
np.save('figure2_coverage.npy', Z)
'''

# when it's already calcualted
Z = np.load('figure2_coverage.npy')
total_percentage = len(Z[Z > 0]) / npts * 100
print('coverage_selected = %.2f %%' % total_percentage)

fig = plt.figure(num=None, figsize=(8, 6), dpi=600, edgecolor='k')
ax = plt.axes(projection=ccrs.Mollweide(central_longitude=0))
ax.coastlines()
ax.set_global()
ctr = ax.contourf(X, Y, Z, cmap='grey', alpha=0.8,
                  transform=ccrs.PlateCarree(central_longitude=0),
                  transform_first=True)
