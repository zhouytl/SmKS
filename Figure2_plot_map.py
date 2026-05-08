#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 31 16:29:30 2025

@author: zhouyangtianli
"""


import pyproj
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
from matplotlib.colors import LinearSegmentedColormap
from cartopy import crs as ccrs
from raypath_utils import cal_raypath, cal_pierce


projection = pyproj.Geod(ellps='WGS84')
model_prem = TauPyModel(model="prem")


# ============================================================================
# The following cal_pierce() function has been moved to raypath_utils.py
# It is kept here as a reference/backup. Use import from raypath_utils instead.
# ============================================================================
# def cal_pierce(latS, lonS, depS, latR, lonR, phase):
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


def hex_to_kml_color(hex_color, alpha='ff'):
    """Converts a hex color (e.g., '#RRGGBB') to KML's AABBGGRR format."""
    hex_color = hex_color.lstrip('#')
    bb = hex_color[4:6]
    gg = hex_color[2:4]
    rr = hex_color[0:2]
    return f"{alpha}{bb}{gg}{rr}"


def plot_group_raypath(df_groups, df_traces, np_coverage):
    colors = ["white", 'white', 'grey']
    custom_cmap = LinearSegmentedColormap.from_list("my_custom_cmap", colors)
    fig = plt.figure(num=None, figsize=(8, 6), dpi=600, edgecolor='k')
    ax = fig.add_subplot(projection=ccrs.Mollweide(central_longitude=150))
    ax.coastlines()
    ax.set_global()
    lon_list = np.arange(-180, 181, 2)
    lat_list = np.arange(-90, 91, 2)
    X, Y = np.meshgrid(lon_list, lat_list)
    Z = np_coverage
    levels = np.linspace(0.0, 1.0, 4)
    ax.contourf(X, Y, Z, cmap=custom_cmap, alpha=0.5, levels=levels,
                transform=ccrs.PlateCarree(central_longitude=0))
    ax.scatter(df_traces.stlo, df_traces.stla, marker='^',
               c='w', s=7, edgecolor='k', linewidth=0.5,
               transform=ccrs.PlateCarree(central_longitude=0), zorder=1)
    ax.scatter(df_groups.evlo, df_groups.evla, marker='*', s=100,
               c='w', edgecolor='k', linewidth=1,
               transform=ccrs.PlateCarree(central_longitude=0), zorder=4)
    for idx, row in df_groups.iterrows():
        evla = row.evla
        evlo = row.evlo
        stla = row.stla
        stlo = row.stlo
        raypath = cal_raypath(evla, evlo, stla, stlo)
        raypath = np.array(raypath)
        raypath_west = raypath[raypath[:, 0] < 0]
        raypath_east = raypath[raypath[:, 0] > 0]
        if row.new < 1:
            c = '#FF2200' #'#FF5910'
            a = 0.8
        else:
            c = 'mediumblue'
            a = 1.0
        if len(raypath_west) > 0:
            ax.plot(raypath_west[:, 0], raypath_west[:, 1],
                    c=c, linewidth=1.0, alpha=a, zorder=2,
                    transform=ccrs.PlateCarree(central_longitude=0))
        if len(raypath_east) > 0:
            ax.plot(raypath_east[:, 0], raypath_east[:, 1],
                    c=c, linewidth=1.0, alpha=a, zorder=2,
                    transform=ccrs.PlateCarree(central_longitude=0))
    plt.tight_layout()
    fig.savefig('figure2_map.pdf')

# read trace coverage
np_coverage = np.load('figure2_coverage.npy')
np_coverage = np_coverage[:, :, 2]
# read station location
df_traces = pd.read_csv('../Data/df_all_measurements.csv')
df_traces = df_traces[(df_traces.selected>0) & (df_traces.group>-1)]
# read group raypath
df_groups = pd.read_csv('../Data/df_all_groups.csv')
plot_group_raypath(df_groups, df_traces, np_coverage)
