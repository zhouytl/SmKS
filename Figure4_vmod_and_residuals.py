#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 14:07:53 2026

@author: zhouyangtianli
"""

from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from netCDF4 import Dataset
import netCDF4 as nd
from cartopy import crs as ccrs
from scipy.interpolate import RegularGridInterpolator
from matplotlib.colors import LinearSegmentedColormap
from glob import glob
import matplotlib.gridspec as gridspec
from scipy import stats

# Blue:      #002D72
# Orange:    #FF5910

cmap_red = LinearSegmentedColormap.from_list("red_white", ["#FF7A3B", "#FFDCC7"])
cmap_red1 = LinearSegmentedColormap.from_list("red_white", ["#FF5910", "#FFDCC7", "#FF5910"])


# cmap_grey = LinearSegmentedColormap.from_list("black_white", ["indianred", "white"])


def ftest(df):
    data1 = pd.read_csv(df).residual3
    data2 = pd.read_csv(df).residuals
    N = len(data1)
    B = 1000  # number of bootstrap samples
    
    delta = []
    
    for _ in range(B):
        # sample indices with replacement
        idx = np.random.choice(N, size=N, replace=True)
        
        # compute RSS for this bootstrap sample
        rss1 = np.sum(data1[idx]**2)
        rss2 = np.sum(data2[idx]**2)
        
        delta.append(rss1 - rss2)
    
    delta = np.array(delta)
    
    # Results
    mean_delta = np.mean(delta)
    ci_lower = np.percentile(delta, 2.5)
    ci_upper = np.percentile(delta, 97.5)
    prob_B_better = np.mean(delta > 0)
    
    print("Mean ΔRSS:", mean_delta)
    print("95% CI:", [ci_lower, ci_upper])
    print("P(Model 2 better):", prob_B_better)
    return mean_delta, ci_lower, ci_upper, prob_B_better



def plot_residuals(dfdir, ax):
    ax.plot([115, 180], [0, 0], c='k')
    t32_list = []
    std_list = []
    gcarc_list1 = []
    df = pd.read_csv(dfdir)
    for idx, row in df.iterrows():
        t32_list.append(row.residuals)
        std_list.append(row.residual_stds)
        gcarc_list1.append(row.gcarc)
    ax.scatter(df.gcarc, df.residuals, s=20, marker='o',
               edgecolor='darkblue', facecolor='#FF5910', zorder=1) # "#FFBC91"
    ax.errorbar(x=df.gcarc, y=df.residuals,
                 yerr=df.residual_stds, xerr=df.gcarc_std, c='darkblue',
                 ls='none', zorder=0)
    mean = np.mean(np.array(t32_list))
    uncertainty = np.median(np.array(std_list))
    print(uncertainty)
    error = np.sum(np.power(t32_list-mean, 2))/len(t32_list)
    rss = np.sum(np.power(np.array(t32_list), 2))
    print(rss)

    ax.grid()
    ax.set_ylim(-2.5, 2.5)
    ax.set_xlim(118, 180)
    ax.set_xlabel('Distance (°)')
    ax.set_ylabel('Residual (s)')


def plot_regional_vmod(vmoddir, ax1):
    data = nd.Dataset(vmoddir)
    lon_list = np.arange(-180, 181, 2)
    lat_list = np.arange(-90, 91, 2)
    X, Y = np.meshgrid(lon_list, lat_list)
    Z1 = data['dvp'][0, :, :]
    ax1.coastlines()
    ax1.set_global()
    ctr = ax1.contourf(X, Y, Z1, cmap=cmap_red,
                       vmin=-0.1, vmax=0, levels=200,
                       transform=ccrs.PlateCarree(central_longitude=0))
    cbar = fig.colorbar(mappable=ctr, ax=ax1,
                        orientation='horizontal',
                        location='bottom', pad=0.05, shrink=0.5)
    cbar.set_ticks([-0.1, 0.0])
    cbar.set_label('P-wave Velocity Variation (%)')
    plt.tight_layout()

    dvp_pmean = []
    dvp_nmean = []
    deplist = data['depth'][:]
    for i in np.arange(len(deplist)):
        dvp_array = data['dvp'][i, :, :]
        dvp_positive = dvp_array[dvp_array > 0]
        dvp_negative = dvp_array[dvp_array < 0]
        dvp_pmean.append(np.mean(dvp_positive))
        dvp_nmean.append(np.mean(dvp_negative))


def plot_global_vmod(vmoddir, ax1):
    
    data = nd.Dataset(vmoddir)
    lon_list = np.arange(-180, 181, 20)
    lat_list = np.arange(-90, 91, 20)
    X, Y = np.meshgrid(lon_list, lat_list)
    Z = np.ones((len(lat_list), len(lon_list))) * -0.1
    ax1.coastlines()
    ax1.set_global()
    ctr = ax1.pcolormesh(X, Y, Z,  alpha=0.5,
                         transform=ccrs.PlateCarree(central_longitude=0),
                         vmin=-0.1, vmax=0.0, rasterized=True,
                         cmap=cmap_red) 
    cbar = fig.colorbar(mappable=ctr, ax=ax1,
                        orientation='horizontal',
                        location='bottom', pad=0.05, shrink=0.5)
    cbar.set_ticks([-0.1, 0.0])
    # plt.colorbar()
    cbar.set_label('P-wave Velocity Variation (%)')
    plt.tight_layout()

    dvp_pmean = []
    dvp_nmean = []
    deplist = data['depth'][:]
    for i in np.arange(len(deplist)):
        dvp_array = data['dvp'][i, :, :]
        dvp_positive = dvp_array[dvp_array > 0]
        dvp_negative = dvp_array[dvp_array < 0]
        dvp_pmean.append(np.mean(dvp_positive))
        dvp_nmean.append(np.mean(dvp_negative))


def plot_torus_vmod(vmoddir, ax1):
    data = nd.Dataset(vmoddir)
    lon_list = np.arange(-180, 181, 1)
    lat_list = np.arange(-90, 91, 1)
    X, Y = np.meshgrid(lon_list, lat_list)
    Z1 = data['dvp'][0, :, :]
    ax1.coastlines()
    ax1.set_global()
    ctr = ax1.contourf(X, Y, Z1, cmap=cmap_red1,
                       vmin=-0.3, vmax=0.3, levels=20, 
                       transform=ccrs.PlateCarree(central_longitude=0))
    cbar = fig.colorbar(mappable=ctr, ax=ax1,
                        orientation='horizontal',
                        location='bottom', pad=0.05, shrink=0.5)
    cbar.set_ticks([-0.3, 0.0])
    cbar.set_label('P-wave Velocity Variation (%)')
    plt.tight_layout()
    
    dvp_pmean = []
    dvp_nmean = []
    deplist = data['depth'][:]
    # print()
    for i in np.arange(len(deplist)):
        dvp_array = data['dvp'][i, :, :]
        dvp_positive = dvp_array[dvp_array > 0]
        dvp_negative = dvp_array[dvp_array < 0]
        dvp_pmean.append(np.mean(dvp_positive))
        dvp_nmean.append(np.mean(dvp_negative))
    
vmoddir_t = 'Codes_partial_layer/core_mod_torus_low_velocity.nc'
vmoddir_p = 'Codes_partial_layer/core_mod_partial_low_velocity.nc'
vmoddir_g = 'Codes_partial_layer/core_mod_global_low_velocity.nc'
dfdir = '../Data/df_all_groups.csv'
dfdira = '../Data/df_all_groups_a.csv'
dfdirb = '../Data/df_all_groups_b.csv'
dfdirc = '../Data/df_all_groups_c.csv'
fig = plt.figure(num=None, figsize=(8, 8), dpi=200, edgecolor='k')
G = gridspec.GridSpec(3, 3)
ax1 = fig.add_subplot(G[0, 0], projection=ccrs.Mollweide(central_longitude=120))
ax2 = fig.add_subplot(G[0, 1:3])
ax3 = fig.add_subplot(G[1, 0], projection=ccrs.Mollweide(central_longitude=120))
ax4 = fig.add_subplot(G[1, 1:3])
ax5 = fig.add_subplot(G[2, 0], projection=ccrs.Mollweide(central_longitude=120))
ax6 = fig.add_subplot(G[2, 1:3])
plot_global_vmod(vmoddir_g, ax1)
plot_residuals(dfdirb, ax2)
plot_torus_vmod(vmoddir_t, ax3)
plot_residuals(dfdira, ax4)
plot_regional_vmod(vmoddir_p, ax5)
plot_residuals(dfdirc, ax6)

_, _, _, proba = ftest(dfdira)
_, _, _, probb = ftest(dfdirb)
_, _, _, probc = ftest(dfdirc)
ax2.text(165, 1.5, 'P(better)=%.2f' % probb)
ax4.text(165, 1.5, 'P(better)=%.2f' % proba)
ax6.text(165, 1.5, 'P(better)=%.2f' % probc)
plt.tight_layout()
fig.savefig('figure4_vmodtests.pdf')

plt.show()