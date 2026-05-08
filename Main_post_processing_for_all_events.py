#!/usr/bin/env python3

# %% sum all files
import pandas as pd
from glob import glob

label = ''
# _a, _b, _c

fsta_list = glob('../Data/20*/df_measure_grouped%s.csv' % label)
df_stas = pd.read_csv(fsta_list[0])
for fsta in fsta_list[1:]:
    df_new = pd.read_csv(fsta)
    df_stas = pd.concat([df_stas, df_new])
df_stas.to_csv('../Data/df_all_measurements%s.csv' % label)
df_stas = df_stas[df_stas.group>-1]
print(df_stas)


# %%

import pandas as pd
from glob import glob

label = ''
# _a, _b, _c
fgrp_list = glob('../Data/20*/df_groups%s.csv' % label)
df_groups = pd.read_csv(fgrp_list[0])
for fgrp in fgrp_list[1:]:
    df_new = pd.read_csv(fgrp)
    df_groups = pd.concat([df_groups, df_new])
df_groups.to_csv('../Data/df_all_groups%s.csv' % label)
print(df_groups)



# %% calculate and plot coverage
import pandas as pd
from raypath_utils import cal_coverage
from visualization_utils import plot_coverage

df_traces = pd.read_csv('../Data/df_all_measurements.csv')
df_selected_traces = df_traces[(df_traces.group>-1)]
df_selected_traces = df_selected_traces.reset_index(drop=True)
np_coverage = cal_coverage(df_selected_traces=df_selected_traces, saven='figure2_coverage.npy')
plot_coverage(np_coverage[:, :, 0], np_coverage[:, :, 1], np_coverage[:, :, 2])

# %% sum groups

from selection_utils import sum_groups_merge3
event_directory = '../Data/TEST_DATASET'
dfname = '%s/df_measure_grouped.csv' % event_directory
fdata = '%s/np_waveforms_merge3.npy' % event_directory
fhypo = '%s/hypo.csv' % event_directory
figdir = '%s/Figures/groups' % event_directory
fgrp = '%s/df_groups.csv' % event_directory
# dfname = '%s/df_measure_grouped_a.csv' % event_directory
# fgrp = '%s/df_groups.csv' % event_directory
sum_groups_merge3(dfname=dfname, fdata=fdata, fhypo=fhypo, figdir=figdir, fgrp=fgrp)

# %% plot all measurements
