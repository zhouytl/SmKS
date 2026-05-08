#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
zhou yangtianli
"""
import pandas as pd

# %% auto selection
from selection_utils import auto_select

# FIXME: Only individual/solo measurement measured SNR not the Pair measurement.
event_directory = '../Data/TEST_DATASET'
objlist = ['%s/Figures/individual_0' % event_directory,
           '%s/Figures/synchronized_1_' % event_directory,
           '%s/Figures/synchronized_2_' % event_directory]
auto_select(evtdir=event_directory,
            fn_measure="df_measure_merge3.csv",
            objlist=objlist)
# FIXME: cannot redo the sync


# %%  Mannual Selection
# Now there need some manual selection
# Build two folders under the measurement directory: /good and /bad.
# Then move the unselected figures into the /bad folder, and move the selected figures into the /good folder.
# After that, run the following code to catagorize the figures and save the results in a csv file.

from selection_utils import sync_dirs
event_directory = '../Data/TEST_DATASET'
reference_dir = '%s/Figures/synchronized_2_' % event_directory
object_dir = '%s/Figures/individual_0' % event_directory
sync_dirs(reference_dir, object_dir)

# %% summarize selection
from selection_utils import catagorize_figures
event_directory = '../Data/TEST_DATASET'
fn_input = '%s/df_measure_merge3.csv' % event_directory
fn_output = '%s/df_measure_selected.csv' % event_directory
directory = '%s/Figures/synchronized_2_' % (event_directory)
#df_all = pd.read_csv('%s/df_measure_merge3.csv' % event_directory)
df_measure = catagorize_figures(fn_input=fn_input, fn_output=fn_output, ref_directory=directory)
# FIXME: df_measure = catagorize_figures(directory, fn_input, fn_output)
# save to df_measure_selected
# should be import from selection_utils

# %% group the selected traces
from selection_utils import group_traces
event_directory = '../Data/TEST_DATASET'
fout = '%s/df_measure_grouped.csv' % event_directory
fname = '%s/df_measure_selected.csv' % event_directory
figdir = '%s/Figures/grouping.pdf' % event_directory
group_traces(fout, fname, figdir)
# group the traces
# summarize all the groups

# %%
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
# %%
