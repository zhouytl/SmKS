#!usr/bin/env python3

# %%

import pandas as pd

df = pd.read_csv('../Data/df_all_measurements.csv')
print(len(df))
df_selected = df[(df.selected>0)&(df.group>-1)]
print(len(df_selected))



# %%
from selection_utils import group_traces
event_directory = '../Data/2003-05-26-mw68-mindanao-philippines'
fout = '%s/df_measure_grouped.csv' % event_directory
fname = '%s/df_measure_selected.csv' % event_directory
figdir = '%s/Figures/grouping.pdf' % event_directory
group_traces(fout, fname, figdir)


# %%
from selection_utils import sum_groups_merge3
event_directory = '../Data/2003-05-26-mw68-mindanao-philippines'
dfname = '%s/df_measure_grouped.csv' % event_directory
fdata = '%s/np_waveforms_merge3.npy' % event_directory
fhypo = '%s/hypo.csv' % event_directory
figdir = '%s/Figures/groups' % event_directory
fgrp = '%s/df_groups.csv' % event_directory
# dfname = '%s/df_measure_grouped_a.csv' % event_directory
# fgrp = '%s/df_groups.csv' % event_directory
sum_groups_merge3(dfname=dfname, fdata=fdata, fhypo=fhypo, figdir=figdir, fgrp=fgrp)
# %

# %% add new measurement to group
from data_utils import add_group_info
label = 'a'
event_directory = '../Data/2003-05-26-mw68-mindanao-philippines'
fname1 = '%s/df_measure_grouped.csv' % event_directory
fname2 = '%s/df_measure_merge4%s.csv' % (event_directory, label)
fout = '%s/df_measure_grouped_%s.csv' % (event_directory, label)
add_group_info(fref=fname1, ftarget=fname2, fout=fout)

# %%
from selection_utils import sum_groups_merge4
event_directory = '../Data/2003-05-26-mw68-mindanao-philippines'
label = 'a'
dfname = '%s/df_measure_grouped_%s.csv' % (event_directory, label)
fdata = '%s/np_waveforms_merge4%s.npy' % (event_directory, label)
fhypo = '%s/hypo.csv' % event_directory
figdir = '%s/Figures/groups_%s' % (event_directory, label)
fgrp = '%s/df_groups_%s.csv' % (event_directory, label)
# dfname = '%s/df_measure_grouped_a.csv' % event_directory
# fgrp = '%s/df_groups.csv' % event_directory
sum_groups_merge4(dfname=dfname, fdata=fdata, fhypo=fhypo, figdir=figdir, fgrp=fgrp)


# %%
from selection_utils import sum_groups_merge3
event_directory = '../Data/2010-07-24-mw66-mindanao-philippines'
dfname = '%s/df_measure_grouped.csv' % event_directory
fdata = '%s/np_waveforms_merge3.npy' % event_directory
fhypo = '%s/hypo.csv' % event_directory
figdir = '%s/Figures/groups' % event_directory
fgrp = '%s/df_groups.csv' % event_directory
# dfname = '%s/df_measure_grouped_a.csv' % event_directory
# fgrp = '%s/df_groups.csv' % event_directory
sum_groups_merge3(dfname=dfname, fdata=fdata, fhypo=fhypo, figdir=figdir, fgrp=fgrp)
# %%
