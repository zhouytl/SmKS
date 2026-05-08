#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  3 15:35:01 2026

@author: zhouyangtianli
"""

from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


eventdir_list = glob('../Data/20*')

fig = plt.figure(figsize=(8, 10), dpi=600)
gs = fig.add_gridspec(1, 6)
ax1 = fig.add_subplot(gs[:, 0:5])
ax2 = fig.add_subplot(gs[:, 5:6])
time = np.arange(2000)*0.1 - 50
for eventdir in eventdir_list:
    df_groups = pd.read_csv('%s/df_groups.csv' % eventdir)
    df_traces = pd.read_csv('%s/df_measure_grouped.csv' % eventdir)
    np_waveforms = np.load('%s/np_waveforms_merge3.npy' % eventdir)
    for idx, row in df_groups.iterrows():
        df_selected = df_traces[df_traces.group == row.group]
        max_snr = np.max(df_selected.snr.values)
        df_best_trace = df_selected[df_selected.snr == max_snr]
        tridx = df_best_trace.tridx.values[0]
        gcarc = df_best_trace.gcarc.values[0]
        trace_obs = np_waveforms[:, int(tridx), 0]
        trace_obs = trace_obs/np.max(np.abs(trace_obs))
        trace_simu3d = np_waveforms[:, int(tridx), 2]
        trace_simu3d = trace_simu3d/np.max(np.abs(trace_simu3d))
        ax1.plot(time, gcarc + 2.0*trace_obs, linewidth=1,
                 c='mediumblue', zorder=1)
        ax1.plot(time, gcarc + 2.0*trace_simu3d, linewidth=2.0, c='#FF5910',
                 alpha=1, zorder=0)
        ax2.errorbar(df_best_trace.t32_fw2, df_best_trace.gcarc, fmt='.',
                     xerr=1/np.sqrt(2)/df_best_trace.snr.values/2/np.pi/0.1,
                     color='#FF5910', ecolor='k', zorder=0)
        ax2.scatter(df_best_trace.t32_fw2, df_best_trace.gcarc,
                    s=15, c='#FF5910', edgecolor='k', zorder=1)
ax2.plot([0, 0], [115, 185], c='k')
ax1.set_ylim(118, 182)
ax1.set_xlim(-50, 100)
#ax1.set_xlabel('Time w.r.t SKKS (s)', fontname="Times New Roman")
ax2.set_ylim(118, 182)
ax2.set_xlim(-2.0, 2.0)
ax2.set_yticks([])
plt.tight_layout()
fig.savefig('waveforms.pdf')









