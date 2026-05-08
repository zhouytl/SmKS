#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 25 14:51:41 2026

@author: zhouyangtianli
"""

import pandas as pd
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
import pyproj
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
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

df_list = glob('../Data/20*/df_groups.csv')
fig = plt.figure(figsize=(5, 5), dpi=600)
ax1 = fig.add_subplot(111)
t32_list = []
temp = 0
for dfname in df_list:
    df = pd.read_csv(dfname)
    temp = temp + len(df)
    for idx, row in df.iterrows():
        residual = row.residual3
        t32_list.append(residual)
        latR = row.stla
        lonR = row.stlo
        depR = 0.0  # km
        latS = row.evla
        lonS = row.evlo
        depS = row.evdp
        latPin_skks, lonPin_skks, latPout_skks, lonPout_skks = cal_pierce(
            latS, lonS, depS, latR, lonR, depR, phase='SKKS')
        raypath = cal_raypath(latPin_skks, lonPin_skks,
                              latPout_skks, lonPout_skks)
        M, N = raypath.shape
        lat_start = raypath[0, 1]
        for i in np.arange(1, M):
            lat_end = raypath[i, 1]
            ax1.plot([residual, residual], [lat_start, lat_end], c='b')
            lat_start = lat_end


ax1.set_ylim(-90, 90)
ax1.set_xlim(-2, 2)
mean = np.mean(t32_list)
ax1.plot([-90, 90], [mean, mean], 'k:')

ax1.set_ylabel('Latitude (°)')
ax1.set_xlabel('Residual (s)')