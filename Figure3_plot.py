#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  4 21:55:22 2026

@author: zhouyangtianli
"""


import pandas as pd
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
from obspy.taup import TauPyModel
from scipy.signal import savgol_filter
import matplotlib.gridspec as gridspec

window_length = 5
polyorder = 3

modlist = ['EPOC', 'KHOMC', 'ek137', 'CCMOC', 'best-fit']
#colorlist = ['gray', 'gray', 'gray', 'gray', '#FF5910'] # ['royalblue', 'royalblue', 'royalblue', 'royalblue', 'purple']
# colorlist = ['#FF5910', '#FF5910', '#FF5910', '#FF5910' ,'#FF5910'] '#FF7A3B'
colorlist = ['k', 'k', 'k', 'k', '#FF5910']
linelist = ['-', '--', ':', '-.', '-']

dep_list = np.linspace(2891, 5151, 500)

fig = plt.figure(figsize=(8, 6), dpi=200)
G = gridspec.GridSpec(4, 4)
ax1 = fig.add_subplot(G[0:4, 0])
ax2 = fig.add_subplot(G[0:2, 1:4])
ax3 = fig.add_subplot(G[2:4, 1:4])
ax1.invert_yaxis()
ax1.grid(zorder=0)
ax2.grid(zorder=0)
ax3.grid(zorder=0)

df_prem = pd.read_csv('../Data/outercore.csv')
vp_prem_list = np.interp(dep_list, df_prem.depth, df_prem.vp)
vp_prem_list_sm = savgol_filter(vp_prem_list, window_length, polyorder)


# calculate theoretical PREM
gcarcs = np.arange(115, 181, 1)
gcarcN = len(gcarcs)
model_prem = TauPyModel(model="prem")
t32_prem = np.zeros(gcarcN)
for i in np.arange(gcarcN):
    arrivals_prem_2k = model_prem.get_travel_times(
        source_depth_in_km=500,
        distance_in_degree=gcarcs[i],
        phase_list=["SKKS"])
    arrivals_prem_3k = model_prem.get_travel_times(
        source_depth_in_km=500,
        distance_in_degree=gcarcs[i],
        phase_list=["SKKKS"])
    t32_prem[i] = arrivals_prem_3k[0].time - arrivals_prem_2k[0].time


for k in np.arange(len(modlist)):
    modname = modlist[k]
    model = TauPyModel(model='Codes_vmod/%s.npz' % modname)
    df_mod = pd.read_csv('Codes_vmod/%s.csv' % modname)
    vp_mod_list = np.interp(dep_list, df_mod.depth, df_mod.vp)
    vp_mod_list_sm = savgol_filter(vp_mod_list, window_length, polyorder)
    t32 = np.zeros(gcarcN)
    for i in np.arange(gcarcN):
        arrivals_2k = model.get_travel_times(
            source_depth_in_km=500,
            distance_in_degree=gcarcs[i],
            phase_list=["SKKS"])
        arrivals_3k = model.get_travel_times(
            source_depth_in_km=500,
            distance_in_degree=gcarcs[i],
            phase_list=["SKKKS"])
        t32[i] = arrivals_3k[0].time - arrivals_2k[0].time
    ax1.plot(vp_mod_list_sm-vp_prem_list_sm, dep_list-2891,
             label=modname, c=colorlist[k], alpha=0.8, linestyle=linelist[k], zorder=2)
    ax2.plot(gcarcs, t32-t32_prem, c=colorlist[k], alpha=0.8, linestyle=linelist[k], zorder=2)
    ax3.plot(gcarcs, t32-t32_prem, c=colorlist[k], alpha=0.8, linestyle=linelist[k], zorder=2)


ax1.set_ylabel('Depth below CMB (km)', font='Times New Roman')
ax1.set_xlabel('dVp (km/s)', font='Times New Roman')
ax1.xaxis.set_label_position('bottom')
ax1.tick_params(labeltop=False, labelbottom=True)
ax1.set_ylim(1000, 0)
ax1.legend(ncol=1, loc='lower left',
           prop={'family': 'Times New Roman', 'size': 8})
ax1.set_title('(a)', fontname='Times New Roman')


df_group = pd.read_csv('../Data/df_all_groups.csv')
df_new = df_group[df_group.new < 1]
df_old = df_group[df_group.new > 0]


mean_old = np.mean(df_old.residualp)
uncertainty_old = np.mean(df_old.residual_stdp)
mean = np.mean(df_group.residual3)
std = np.std(df_group.residual3)
rss = np.sum(np.power(df_group.residual3, 2))
print(rss)
print(std)
uncertainty = np.mean(df_group.residual_std3)
mean_new = np.mean(df_new.residual3)

ax2.plot([115, 180], [0, 0], c='k')


ax3.plot([115, 180], [0, 0], c='k')

ax2.scatter(df_old.gcarc, df_old.residualp, s=20, marker='o',
            edgecolor='mediumblue', facecolor='#0070FF', zorder=3)
ax2.errorbar(x=df_old.gcarc, y=df_old.residualp, fmt='none',
             yerr=df_old.residual_stdp, xerr=df_old.gcarc_std, c='mediumblue',
             ls='none', zorder=2)

ax3.scatter(df_old.gcarc, df_old.residual3, s=20, marker='o',
            edgecolor='darkblue', facecolor='#0070FF', zorder=3)
ax3.errorbar(x=df_old.gcarc, y=df_old.residual3,
             yerr=df_old.residual_std3, xerr=df_old.gcarc_std, c='darkblue',
             ls='none', zorder=2)

ax3.scatter(df_new.gcarc, df_new.residual3, s=20, marker='o',
            edgecolor='darkblue', facecolor='#FF5910', alpha=1, zorder=3)
ax3.errorbar(x=df_new.gcarc, y=df_new.residual3, fmt='none',
             yerr=df_new.residual_std3, xerr=df_new.gcarc_std, c='darkblue',
             alpha=0.8,
             ls='none', zorder=2)

#'#D7490D' "#FFBC91"

#ax3.fill_between(x=[118, 180],
#                 y1=mean-uncertainty,
#                 y2=mean+uncertainty,
#                 color='k', alpha=0.1)


for label in ax1.get_xticklabels() + ax1.get_yticklabels():
    label.set_fontname('Times New Roman')
for label in ax2.get_xticklabels() + ax2.get_yticklabels():
    label.set_fontname('Times New Roman')
for label in ax3.get_xticklabels() + ax3.get_yticklabels():
    label.set_fontname('Times New Roman')

ax2.set_xticklabels([])
ax2.set_ylabel('Residual (s)', font='Times New Roman')
ax2.yaxis.set_label_position('right')
ax2.yaxis.set_ticks_position('right')
ax2.tick_params(labelleft=False, labelright=True)
ax2.set_ylim(-2.0, 2.5)
ax2.set_xlim(118, 180)
ax2.set_title('(b)', fontname='Times New Roman')

ax3.set_xlabel('Distance (°)', font='Times New Roman')
ax3.set_ylabel('Residual (s)', font='Times New Roman')
ax3.yaxis.set_label_position('right')
ax3.yaxis.set_ticks_position('right')
ax3.set_ylim(-2.0, 2.5)
ax3.set_xlim(118, 180)
ax3.set_title('(c)', fontname='Times New Roman')

plt.tight_layout( )
plt.show()
#plt.subplots_adjust(wspace=0.1, hspace=0.1)
fig.savefig('figure3_residuals.pdf')
