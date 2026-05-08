#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 25 14:46:28 2026

@author: zhouyangtianli
"""

import numpy as np
import pandas as pd
import netCDF4 as nd
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
import pyproj
import cartopy.feature as cfeature
from cartopy import crs as ccrs
from raypath_utils import cal_raypath, cal_pierce


projection = pyproj.Geod(ellps='WGS84')
model_prem = TauPyModel(model="prem")


# ============================================================================
# The following cal_pierce() function has been moved to raypath_utils.py
# It is kept here as a reference/backup. Use import from raypath_utils instead.
# ============================================================================
# def cal_pierce(latS, lonS, depS, latR, lonR, depR, phase):
#     az_SR, baz_SR, dist_SR_km = projection.inv(lonS, latS, lonR, latR)
#     gcarc = locations2degrees(latS, lonS, latR, lonR)
#     pierces_prem = model_prem.get_pierce_points(source_depth_in_km=depS,
#                                                 distance_in_degree=gcarc,
#                                                 phase_list=[phase])
#     if len(pierces_prem) > 0:
#         path = pierces_prem[0].pierce
#         pierces_points = [list(item) for item in path]
#         pcmb = []
#         for ppoint in pierces_points:
#             if ppoint[3] == 2891:
#                 pcmb.append(ppoint)
#
#         pcmb_in = pcmb[0]
#         pcmb_out = pcmb[-1]
#         angle_pcmb_in = 180*pcmb_in[2]/np.pi
#         angle_pcmb_out = 180*pcmb_out[2]/np.pi
#         dist_in_km = dist_SR_km*angle_pcmb_in/gcarc
#         dist_out_km = dist_SR_km*angle_pcmb_out/gcarc
#
#         lonPin, latPin, bazPin = projection.fwd(lonS, latS,
#                                                 az_SR, dist_in_km)
#         lonPout, latPout, bazPout = projection.fwd(lonS, latS,
#                                                    az_SR, dist_out_km)
#     else:
#         latPin = np.nan
#         lonPin = np.nan
#         latPout = np.nan
#         lonPout = np.nan
#     return latPin, lonPin, latPout, lonPout
    else:
        latPin = np.nan
        lonPin = np.nan
        latPout = np.nan
        lonPout = np.nan
    return latPin, lonPin, latPout, lonPout



def plot_global_map_core(df_measurement):
    cmap = plt.cm.rainbow
    norm = colors.Normalize(vmin=-0.1, vmax=0.5)
    data = nd.Dataset('../Data/velocity_models/SP12RTS_percent.nc')
    lon_list = np.arange(-180, 181, 1)
    lat_list = np.arange(-90, 91, 1)
    X, Y = np.meshgrid(lon_list, lat_list)
    Z = data['dvs'][-1, :, :]

    fig = plt.figure(num=None, figsize=(8, 6), dpi=600, edgecolor='k')
    ax = plt.axes(projection=ccrs.AzimuthalEquidistant(central_longitude=0,
                                                       central_latitude=90))
    ax.coastlines()
    ax.set_global()
    ctr = ax.contourf(X, Y, Z, cmap='bwr_r', alpha=0.5,
                      transform=ccrs.PlateCarree(central_longitude=0))
    lon1list = []
    lat1list = []
    lon2list = []
    lat2list = []
    for idx, row in df_measurement.iterrows():

    
        latR = row.stla
        lonR = row.stlo
        depR = 0.0  # km
        latS = row.evla
        lonS = row.evlo
        depS = row.evdp
        latPin_skks, lonPin_skks, latPout_skks, lonPout_skks = cal_pierce(
            latS, lonS, depS, latR, lonR, depR, phase='SKKS')
        latPin_s3ks, lonPin_s3ks, latPout_s3ks, lonPout_s3ks = cal_pierce(
            latS, lonS, depS, latR, lonR, depR, phase='SKKKS')
        #print(latPin_skks, lonPin_skks, latPout_skks, lonPout_skks)
        
        raypath = cal_raypath(latPin_skks, lonPin_skks,
                              latPout_skks, lonPout_skks)
        raypath_west = raypath[raypath[:, 0] < 0]
        raypath_east = raypath[raypath[:, 0] > 0]
        if len(raypath_west) > 0:
            ax.plot(raypath_west[:, 0], raypath_west[:, 1], 
                    c=cmap(norm(row.t32_fw2)), alpha=0.2,
                    transform=ccrs.PlateCarree(central_longitude=0))
        if len(raypath_east) > 0:
            ax.plot(raypath_east[:, 0], raypath_east[:, 1],
                    c=cmap(norm(row.t32_fw2)), alpha=0.2,
                    transform=ccrs.PlateCarree(central_longitude=0))
        lat1list.append(latPin_s3ks)
        lon1list.append(lonPin_s3ks)
        lat2list.append(latPout_s3ks)
        lon2list.append(lonPout_s3ks)
        
    scm = ax.scatter(lon1list, lat1list,
                     c=df_measurement.t32_fw2, s=1, cmap='rainbow', vmin=-0.1, vmax=0.5,
                     transform=ccrs.PlateCarree(central_longitude=0))
    scm = ax.scatter(lon2list, lat2list,
                     c=df_measurement.t32_fw2, s=1,cmap='rainbow', vmin=-0.1, vmax=0.5,
                     transform=ccrs.PlateCarree(central_longitude=0))

    cax2 = fig.add_axes([0.1, 0.0, 0.30, 0.01])
    fig.colorbar(ctr, cax=cax2, orientation='horizontal')
    cax2.set_xticks([-1.6, 0, 1.6], [-1.6, 0, 1.6],
                    fontname='Helvetica')
    cax2.set_xlabel('dVs at CMB (%)', fontname='Helvetica')
    cax2.xaxis.set_ticks_position('bottom')
    cax2.xaxis.set_label_position('top')

    cax3 = fig.add_axes([0.65, 0.0, 0.30, 0.01])
    fig.colorbar(scm, cax=cax3, orientation='horizontal')
    cax3.set_xticks([-0.1, 0.5], [-0.1, 0.5],
                    fontname='Helvetica')
    cax3.set_xlabel('Residual (s)', fontname='Helvetica')
    cax3.xaxis.set_ticks_position('bottom')
    cax3.xaxis.set_label_position('top')
    plt.tight_layout()

df_measure = pd.read_csv('../Data/df_all_measurements.csv')
df_measure = df_measure[df_measure.group>-1]
print(len(df_measure))

plot_global_map_core(df_measure)
