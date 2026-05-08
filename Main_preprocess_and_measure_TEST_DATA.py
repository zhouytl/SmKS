#!usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
This code is used to run one example of observational data processing, which includes the following steps:
1. Standardize the raw data from IRIS Wilber3. 
    OBS_standardize_raw_data_from_wilber.py
2. Rotate the SmKS data from ZNE to RTZ. 
    OBS_rotate_raw_data_from_wiler.py
3. Convert the format of the data from SAC to an numpy array, and save the corresponding headers in a csv file.
    Obs_prepare_data.py
4. Generte station information for data simulation.
    OBS_generate_station_list_for_simulation.py
"""

# %% Prepare

import os
os.environ['LC_ALL'] = 'C.UTF-8'
event_directory = '../Data/TEST_DATASET'

from visualization_utils import plot_smks_features, plot_SmKS_travel_time_table

plot_smks_features(gcarc=120, depth=560)
plot_SmKS_travel_time_table(depth=560)


# %% standardize observational data
from stdobs import prepare_obs_data, standardize_raw_data_from_wilber, rotate_SmKS_data_from_NE_to_RT

event_directory = '../Data/TEST_DATASET'
standardize_raw_data_from_wilber(event_directory)
rotate_SmKS_data_from_NE_to_RT(event_directory)
prepare_obs_data(directory=event_directory,
                  component='R', sample_rate=10,
                  trace_length=400, half_window=8,
                  before_pick=50, after_pick=150)


# %% standardize simulation data Simu3D
from stdsyn import prepare_syn_data, convert_simudata
event_directory = '../Data/TEST_DATASET'
label = 'simu1D'
convert_simudata(event_directory=event_directory, label=label)
prepare_syn_data(directory=event_directory,
                  component='R', sample_rate=10,
                  trace_length=2500, half_window=10,
                  before_pick=50, after_pick=150,
                  label=label)

# %% standardize simulation data Simu3D
from stdsyn import prepare_syn_data, convert_simudata
event_directory = '../Data/TEST_DATASET'
label = 'simu3D'
convert_simudata(event_directory=event_directory, label=label)
prepare_syn_data(directory=event_directory,
                  component='R', sample_rate=10,
                  trace_length=2500, half_window=10,
                  before_pick=50, after_pick=150,
                  label=label)


# %% merge obs, simu1D, and simu3D data
from data_utils import merge3_data
event_directory = '../Data/TEST_DATASET'
merge3_data(directory=event_directory,
           olabel='obs', slabel1='simu1D', slabel2='simu3D',
           sample_rate=10)

# %% measure smks solo residuals
from measure_smks_utils import measure_residual_solo
event_directory = '../Data/TEST_DATASET'
label = 'merge3'
measure_residual_solo(directory=event_directory, label=label,
                        sample_rate=10, before_pick=50,
                        sign_window=8, corr_window=12, peak_window=4, layer=0)

# %% measure smks pair reisiduals for 1D PREM model 
from measure_smks_utils import measure_residual_pair
event_directory = '../Data/TEST_DATASET'
mtype = 'merge3'
label = ''
layer = 1
measure_residual_pair(directory=event_directory,
                        mtype=mtype, label=label, layer=layer,
                        sample_rate=10, before_pick=50,
                        corr_window=8)
# FIXME: measure_reisidual_pair only export df_measure_merge3.csv
# with no difference between layer1 (simu1D) or layer2 (simu3D) 


# %% measure smks pair reisiduals for PREM+SP12RTS model 
from measure_smks_utils import measure_residual_pair
event_directory = '../Data/TEST_DATASET'
mtype = 'merge3'
label = ''
layer = 2
measure_residual_pair(directory=event_directory,
                        mtype=mtype, label=label, layer=layer,
                        sample_rate=10, before_pick=50,
                        corr_window=8)

# %% merge measurements
from data_utils import merge3_measure
event_directory = '../Data/TEST_DATASET'
fn_stations = 'df_stations_merge3.csv'
fn_measure_ind = 'df_measure_individual_0.csv'
fn_measure_syn1 = 'df_measure_synchronized_1_.csv'
fn_measure_syn2 = 'df_measure_synchronized_2_.csv'
fn_output = 'df_measure_merge3.csv'

df_measure = merge3_measure(event_directory=event_directory,
                            fn_stations=fn_stations,
                            fn_measure_ind=fn_measure_ind,
                            fn_measure_syn1=fn_measure_syn1,
                            fn_measure_syn2=fn_measure_syn2,
                            fn_output=fn_output)

