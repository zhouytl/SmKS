
#!usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
    This code is used to run one example of hypothesis test.
    This code is build on top of existing observational data,
and synthetic data based on 1D and 3D models. 
    Files are including 
        np_waveforms_obs.npy
        np_waveforms_simu1d.npy
        np_waveforms_simu3d.npy
The steps including:
1. merge data for hypothesis test

"""

# %% Prepare

import os
os.environ['LC_ALL'] = 'C.UTF-8'


# %% standardize simulation data Simu3Da (Torus Model)
from stdsyn import prepare_syn_data, convert_simudata
event_directory = '../Data/TEST_DATASET'
label = 'simu3Db'
convert_simudata(event_directory=event_directory, label=label)
prepare_syn_data(directory=event_directory,
                  component='R', sample_rate=10,
                  trace_length=2500, half_window=10,
                  before_pick=50, after_pick=150,
                  label=label)


# %% merge data files for Model A (torus model)
from data_utils import merge4_data
label = 'b'
event_directory = '../Data/TEST_DATASET'
merge4_data(directory=event_directory,
            olabel='obs', slabel1='simu1D', slabel2='simu3D',
            slabel3='simu3D%s'%label,
            sample_rate=10, label=label)


# %% measure smks pair reisiduals for Model A (torus model) 
from measure_smks_utils import measure_residual_pair
event_directory = '../Data/TEST_DATASET'
mtype = 'merge4'
label = 'b'
measure_residual_pair(directory=event_directory,
                        mtype=mtype, label=label, layer=3,
                        sample_rate=10, before_pick=50,
                        corr_window=8)

# %% merge measurements
from data_utils import merge4_measure
event_directory = '../Data/TEST_DATASET'
fn_stations = 'df_stations_merge4b.csv'
fn_measure_ind = 'df_measure_individual_0.csv'
fn_measure_syn1 = 'df_measure_synchronized_1_.csv'
fn_measure_syn2 = 'df_measure_synchronized_2_.csv'
fn_measure_syn3 = 'df_measure_synchronized_3_b.csv'
fn_output = 'df_measure_merge4b.csv'

df_measure = merge4_measure(event_directory=event_directory,
                            fn_stations=fn_stations,
                            fn_measure_ind=fn_measure_ind,
                            fn_measure_syn1=fn_measure_syn1,
                            fn_measure_syn2=fn_measure_syn2,
                            fn_measure_syn3=fn_measure_syn3,
                            fn_output=fn_output)


# %% add new measurement to group
from data_utils import add_group_info
event_directory = '../Data/TEST_DATASET'
fname1 = '%s/df_measure_grouped.csv' % event_directory
fname2 = '%s/df_measure_merge4b.csv' % event_directory
fout = '%s/df_measure_grouped_b.csv' % event_directory
add_group_info(fref=fname1, ftarget=fname2, fout=fout)

# %%
from selection_utils import sum_groups_merge4
event_directory = '../Data/TEST_DATASET'
dfname = '%s/df_measure_grouped_b.csv' % event_directory
fdata = '%s/np_waveforms_merge4b.npy' % event_directory
fhypo = '%s/hypo.csv' % event_directory
figdir = '%s/Figures/groups_b' % event_directory
fgrp = '%s/df_groups_b.csv' % event_directory
# dfname = '%s/df_measure_grouped_a.csv' % event_directory
# fgrp = '%s/df_groups.csv' % event_directory
sum_groups_merge4(dfname=dfname, fdata=fdata, fhypo=fhypo, figdir=figdir, fgrp=fgrp)
# %%
