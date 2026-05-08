# Function Introduction

# Utils 
raypath_utils.py

data_unitls.py
measure_smks_utils.py
selection_utils.py

# Main 
Main_preprocess_and_measure_TEST_DATA.py
    standardize observational data.
        df_station_obs.csv
        np_waveforms_obs.npy
    standardize synthetic data (PREM / PREM+SP12RTS).
        df_station_simu1D.csv
        np_waveforms_simu1D.npy
        df_station_simu3D.csv
        np_waveforms_simu3D.npy
    merge obs and syn dataset.
        df_station_merge3.csv 
        *np_waveforms_merge3.npy
    measure in solo.
        df_measure_individual_0.csv
        df_measure_individual_1.csv
        df_measure_individual_2.csv
    measure in pair.
        df_measure_synchronized_1_.csv
        df_measure_synchronized_2_.csv
    merge all measurements:
        *df_measure_merge3.csv

Main_selection_and_group_TEST_DATA.py
    auto selection
    manual selection 
    summarizing the selection result 
        *df_measure_selected.csv
    group the selected traces
        **df_measure_grouped.csv**
    summarize groups
        **df_groups.csv** 

Main_hypothesis_test_TEST_DATA.py
    standardize synthetic data (PREM+SP12RTS+Core).
        np_waveforms_simu3Da.npy
        np_waveforms_simu3Db.npy
        np_waveforms_simu3Dc.npy
    merge obs and syn dataset.
        np_waveforms_merge4a.npy
        np_waveforms_merge4b.npy
        np_waveforms_merge4c.npy
    measure in pairing method.
        df_measure_synchronized_3_a.csv
        df_measure_synchronized_3_b.csv
        df_measure_synchronized_3_c.csv
    mearge the measurements.
        df_measure_merge4a.csv
        df_measure_merge4b.csv
        df_measure_merge4c.csv
    `start from here to update`
    add group information to the measurements
        df_measure_grouped_a.csv
        df_measure_grouped_b.csv
        df_measure_grouped_c.csv
    summarize groups
        **df_groups_a.csv**
        **df_groups_b.csv**
        **df_groups_c.csv**

Main_post_processing_for_all_events.py
    calculate coverage
        df_measure_grouped.csv -> coverage.nd
    summarize all earthquakes grouped result
        __*/df_groups.csv__ -> df_all_groups.csv 
        __*/df_groups_a.csv__ -> df_all_groups_a.csv
        __*/df_groups_b.csv__ -> df_all_groups_b.csv
        __*/df_groups_c.csv__ -> df_all_groups_c.csv
    plot measurements on gcarc v.s. residual, map
        df_all_groups.csv (residual_pp, residual_fw3)
        df_all_groups_a.csv (residuals)
        df_all_groups_b.csv (residuals)
        df_all_groups_c.csv (residuals)
