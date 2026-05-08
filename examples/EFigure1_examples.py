#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 21:27:05 2026

@author: zhouyangtianli
"""


import numpy as np
import pandas as pd
import netCDF4 as nd
import matplotlib.pyplot as plt
import pyproj
from cartopy import crs as ccrs
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
from raypath_utils import cal_raypath


projection = pyproj.Geod(ellps='WGS84')
model_prem = TauPyModel(model="prem")


def cal_pierce_and_bounce(latS, lonS, depS, latR, lonR, phase):

    az_SR, baz_SR, dist_SR_km = projection.inv(lonS, latS, lonR, latR)
    gcarc = locations2degrees(latS, lonS, latR, lonR)
    pierces_prem = model_prem.get_pierce_points(source_depth_in_km=depS,
                                                distance_in_degree=gcarc,
                                                phase_list=[phase])
    path = pierces_prem[0].pierce
    pierces_points = [list(item) for item in path]
    pcmb = []
    for ppoint in pierces_points:
        if ppoint[3] == 2891:
            pcmb.append(ppoint)

    npbp = len(pcmb)
    latPBlist = []
    lonPBlist = []
    for bpidx in np.arange(npbp):
        pb = pcmb[bpidx]
        angle = 180*pb[2]/np.pi
        dist_in_km = dist_SR_km*angle/gcarc
        lonB, latB, bazB = projection.fwd(lonS, latS, az_SR, dist_in_km)
        latPBlist.append(latB)
        lonPBlist.append(lonB)
    return latPBlist, lonPBlist


def plot_geometry_of_two_groups(df1, df2):
    fig = plt.figure(num=None, figsize=(6, 4), dpi=600, edgecolor='k')
    ax = fig.add_subplot(projection=ccrs.Mollweide(central_longitude=150))
    ax.coastlines()
    ax.set_global()
    data = nd.Dataset('../Data/velocity_models/SP12RTS_percent.nc')
    lon_list = np.arange(-180, 181, 1)
    lat_list = np.arange(-90, 91, 1)
    X, Y = np.meshgrid(lon_list, lat_list)
    Z = data['dvs'][-1, :, :]
    ctr = ax.contourf(X, Y, Z, cmap='bwr_r', alpha=0.5,
                      transform=ccrs.PlateCarree(central_longitude=0))
    clb = fig.colorbar(ctr, orientation='horizontal', pad=0.05,
                       shrink=0.7, aspect=40)

    for idx, row in df1.iterrows():
        evla = row.evla
        evlo = row.evlo
        evdp = row.evdp
        stla = row.stla
        stlo = row.stlo
        raypath = cal_raypath(latS=evla, lonS=evlo, latR=stla, lonR=stlo)
        raypath_west = raypath[raypath[:, 0] < 0]
        raypath_east = raypath[raypath[:, 0] > 0]
        if len(raypath_west) > 0:
            ax.plot(raypath_west[:, 0], raypath_west[:, 1],
                    c='k', alpha=0.6, linewidth=1,
                    transform=ccrs.PlateCarree(central_longitude=0))
        if len(raypath_east) > 0:
            ax.plot(raypath_east[:, 0], raypath_east[:, 1],
                    c='k', alpha=0.6, linewidth=1,
                    transform=ccrs.PlateCarree(central_longitude=0))
        latPBskks, lonPBskks = cal_pierce_and_bounce(latS=evla, lonS=evlo,
                                                     depS=evdp,
                                                     latR=stla, lonR=stlo,
                                                     phase='SKKS')
        latPBs3ks, lonPBs3ks = cal_pierce_and_bounce(latS=evla, lonS=evlo,
                                                     depS=evdp,
                                                     latR=stla, lonR=stlo,
                                                     phase='SKKKS')
        ax.scatter(lonPBskks, latPBskks, s=10, marker='s',
                   c='m', edgecolor='k', zorder=2, linewidth=0.5,
                   transform=ccrs.PlateCarree(central_longitude=0))
        ax.scatter(lonPBs3ks, latPBs3ks, s=10, marker='s',
                   c='c', edgecolor='k', zorder=2, linewidth=0.5,
                   transform=ccrs.PlateCarree(central_longitude=0))
        ax.scatter(evlo, evla, s=200,
                   c='r', edgecolor='k', marker='*', zorder=2,
                   transform=ccrs.PlateCarree(central_longitude=0))
        ax.scatter(stlo, stla, s=50,
                   c='b', edgecolor='k', marker='^', zorder=2,
                   transform=ccrs.PlateCarree(central_longitude=0))

        for idx, row in df2.iterrows():
            evla = row.evla
            evlo = row.evlo
            evdp = row.evdp
            stla = row.stla
            stlo = row.stlo
            raypath = cal_raypath(latS=evla, lonS=evlo, latR=stla, lonR=stlo)
            raypath_west = raypath[raypath[:, 0] < 0]
            raypath_east = raypath[raypath[:, 0] > 0]
            if len(raypath_west) > 0:
                ax.plot(raypath_west[:, 0], raypath_west[:, 1],
                        c='k', alpha=0.6, linewidth=1,
                        transform=ccrs.PlateCarree(central_longitude=0))
            if len(raypath_east) > 0:
                ax.plot(raypath_east[:, 0], raypath_east[:, 1],
                        c='k', alpha=0.6, linewidth=1,
                        transform=ccrs.PlateCarree(central_longitude=0))
            latPBskks, lonPBskks = cal_pierce_and_bounce(latS=evla, lonS=evlo,
                                                         depS=evdp,
                                                         latR=stla, lonR=stlo,
                                                         phase='SKKS')
            latPBs3ks, lonPBs3ks = cal_pierce_and_bounce(latS=evla, lonS=evlo,
                                                         depS=evdp,
                                                         latR=stla, lonR=stlo,
                                                         phase='SKKKS')
            ax.scatter(lonPBskks, latPBskks, s=10, marker='s',
                       c='m', edgecolor='k', zorder=2, linewidth=0.5,
                       transform=ccrs.PlateCarree(central_longitude=0))
            ax.scatter(lonPBs3ks, latPBs3ks, s=10, marker='s',
                       c='c', edgecolor='k', zorder=2, linewidth=0.5,
                       transform=ccrs.PlateCarree(central_longitude=0))
            ax.scatter(evlo, evla, s=200,
                       c='r', edgecolor='k', marker='*', zorder=2,
                       transform=ccrs.PlateCarree(central_longitude=0))
            ax.scatter(stlo, stla, s=50,
                       c='blue', edgecolor='k', marker='^', zorder=2,
                       transform=ccrs.PlateCarree(central_longitude=0))
    fig.savefig('figure3_raypath.pdf')


def plot_multiple_residuals(df1, df2):

    fig = plt.figure(figsize=(6, 2), dpi=600)
    ax1 = fig.add_subplot(141)
    ax1.errorbar(df1.gcarc, df1.t32_pp, ecolor='k', fmt='o',
                 markerfacecolor='grey', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df1.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax1.errorbar(df2.gcarc, df2.t32_pp, ecolor='k', fmt='o',
                 markerfacecolor='w', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df2.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax1.plot([140, 150], [0, 0], c='k')
    ax1.grid()
    ax1.set_ylim(-2, 2)
    ax1.set_xlim(140, 150)
    ax1.set_yticks([-1, 0, 1], [-1, 0, 1])
    ax1.set_xticks([142, 145, 148], [142, 145, 148])

    ax2 = fig.add_subplot(142)
    ax2.errorbar(df1.gcarc, df1.t32_cc, ecolor='k', fmt='o',
                 markerfacecolor='grey', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df1.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax2.errorbar(df2.gcarc, df2.t32_cc, ecolor='k', fmt='o',
                 markerfacecolor='w', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df2.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax2.plot([140, 150], [0, 0], c='k')
    ax2.grid()
    ax2.set_ylim(-2, 2)
    ax2.set_xlim(140, 150)
    ax2.set_yticks([-1, 0, 1])
    ax2.set_yticklabels([])
    ax2.set_xticks([142, 145, 148], [142, 145, 148])

    ax3 = fig.add_subplot(143)
    ax3.errorbar(df1.gcarc, df1.t32_fw1, ecolor='k', fmt='o',
                 markerfacecolor='grey', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df1.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax3.errorbar(df2.gcarc, df2.t32_fw1, ecolor='k', fmt='o',
                 markerfacecolor='w', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df2.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax3.plot([140, 150], [0, 0], c='k')
    ax3.grid()
    ax3.set_ylim(-2, 2)
    ax3.set_xlim(140, 150)
    ax3.set_yticks([-1, 0, 1])
    ax3.set_yticklabels([])
    ax3.set_xticks([142, 145, 148], [142, 145, 148])

    ax4 = fig.add_subplot(144)
    ax4.errorbar(df1.gcarc, df1.t32_fw2, ecolor='k', fmt='o',
                 markerfacecolor='grey', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df1.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax4.errorbar(df2.gcarc, df2.t32_fw2, ecolor='k', fmt='o',
                 markerfacecolor='w', markeredgecolor='k',
                 markersize=5,
                 yerr=1/df2.snr/np.sqrt(2)/2/np.pi/0.1,
                 ls='none', zorder=1)
    ax4.plot([140, 150], [0, 0], c='k')
    ax4.set_ylim(-2, 2)
    ax4.grid()
    ax4.set_xlim(140, 150)
    ax4.set_yticks([-1, 0, 1])
    ax4.set_yticklabels([])
    ax4.set_xticks([142, 145, 148], [142, 145, 148])
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.1, hspace=0)
    fig.savefig('figure3_residual.pdf')


def plot_traces(df1, df2, np1, np2):
    fig = plt.figure(figsize=(6, 6), dpi=600)
    ax = fig.add_subplot(111)
    time = np.arange(2000) * 0.1 - 50
    for idx, row in df1.iterrows():
        ax.plot(time, row.gcarc+np1[:, int(row.tridx), 0], c='k', linewidth=.5)
        ax.plot(time, row.gcarc+np1[:, int(row.tridx), 2], c='r', linewidth=.5)
    for idx, row in df2.iterrows():
        ax.plot(time, row.gcarc+np2[:, int(row.tridx), 0], c='k', linewidth=.5)
        ax.plot(time, row.gcarc+np2[:, int(row.tridx), 2], c='g', linewidth=.5)
    ax.set_xlim(-50, 150)
    ax.set_ylim(139, 151)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Distance (°)')


event_directory_1 = '../Data/2007-10-16-mw66-south-of-fiji-islands-1'
df1 = pd.read_csv('%s/df_measure_grouped.csv' % (event_directory_1))
np1 = np.load('%s/np_waveforms_merge3.npy' % event_directory_1)
df1 = df1[(df1.gcarc > 140) & (df1.gcarc < 150)]
df1 = df1[(df1.group == 2) | (df1.group == 6)]

event_directory_2 = '../Data/2020-07-06-mww67-java-sea'
df2 = pd.read_csv('%s/df_measure_grouped.csv' % (event_directory_2))
np2 = np.load('%s/np_waveforms_merge3.npy' % event_directory_2)
df2 = df2[(df2.gcarc > 140) & (df2.gcarc < 150)]
df2 = df2[(df2.group == 5) | (df2.group == 3)]

plot_geometry_of_two_groups(df1, df2)
plot_multiple_residuals(df1, df2)
# plot_traces(df1, df2, np1, np2)







