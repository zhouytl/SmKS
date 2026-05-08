#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 10:34:26 2025

@author: zhouyangtianli
"""

import os
import shutil
import numpy as np
import pandas as pd
from glob import glob
from tqdm import tqdm
from obspy import read
from obspy import Trace

from obspy.geodetics import locations2degrees
from obspy.signal.rotate import rotate2zne, rotate_ne_rt

from obspy.taup import TauPyModel
model_prem = TauPyModel(model="prem")
model = TauPyModel(model='ak135')

import pyproj
projection = pyproj.Geod(ellps='WGS84')


from raypath_utils import cal_dist_time
from visualization_utils import plot_eq_map, plot_data_matrix
from data_utils import read_hypo, matrix_align_slant



def catalogue_raw_channel_from_Wilber(data_directory):
    """
    Catalogue the available channels in the raw data directory.
    When you download the data from IRIS Wilber3, you will get a zip file for all avaliable data.
    Unzip the file and there will be many SAC files with the naming rule: 
        network.station.location.channel.D(not sure what is this).year.jday.HMS.SAC
    This function will list all the available SAC files in the folder and catalogue them in to a dataframe.
    The returning dataframe has four columns: network, station, location, channel. Each row corresponds to one SAC file.
    """
    df_avaliable_data = pd.DataFrame(data=np.zeros((0, 4)),
                                     columns=['network',
                                              'station',
                                              'location',
                                              'channel'])
    file_list = glob('%s/SAC/*.SAC' % data_directory)
    for file_dir in file_list:
        file_name = file_dir.split('/')[-1]
        station_info = file_name.split('.')
        network = station_info[0]
        station = station_info[1]
        location = station_info[2]
        channel = station_info[3]
        row = pd.DataFrame([{'network': network,
                             'station': station,
                             'location': location,
                             'channel': channel}])
        df_avaliable_data = pd.concat([df_avaliable_data, row],
                                      ignore_index=True)
        df_avaliable_data = df_avaliable_data.drop_duplicates()
    return df_avaliable_data


def standerdize_every_station(data_directory, channel_catalog, source_info):
    """
    This function only works for SmKS measurments.
    It will read the raw SAC files from SAC directory,
    and cut between -100 and 300 s along SKKS phase arrival time.
    """
    print(source_info)
    PHASE_CODE = "SKKS"
    OBJECT_DIRECTORY = "SAC"
    OUTPUT_DIRECTORY = "SmKS"
    CUT_BEFORE = 100
    CUT_AFTER = 300
 
    for idx, row in tqdm(channel_catalog.iterrows(),
                         total=channel_catalog.shape[0],
                         desc="Processing DataFrame"):
        os.makedirs('%s/%s' % (data_directory, OUTPUT_DIRECTORY), exist_ok=True)
        short_file_name = "%s/%s/%s.%s.%s.%s" % (data_directory,
                                                OBJECT_DIRECTORY,
                                                row.network,
                                                row.station,
                                                row.location,
                                                row.channel)
        output_file_name = '%s/%s/%s.%s.%s.%s' % (data_directory,
                                                OUTPUT_DIRECTORY,
                                                row.network,
                                                row.station,
                                                row.location,
                                                row.channel)
        file_name = "%s.*" % short_file_name
        files_for_single_channel = glob(file_name)
        if len(files_for_single_channel) > 1:
            """When there are multiple SAC files for the same station and channel,
              we will merge them together."""
            st = read(files_for_single_channel[0])
            for ch in range(len(files_for_single_channel)):
                st = st + read(files_for_single_channel[ch])
            try:
                st = st.merge(method=1, fill_value=0)
            except Exception as e:
                print(e)
                continue
            tr = st[0]
            otime = source_info['otime']
            evla = source_info['evla']
            evlo = source_info['evlo']
            evdp = source_info['evdp']
            stla = tr.stats.sac['stla']
            stlo = tr.stats.sac['stlo']
            gcarc = locations2degrees(evla, evlo, stla, stlo)
            tr.stats.sac['gcarc'] = gcarc
            arrivals_PHASE = model.get_travel_times(source_depth_in_km=evdp,
                                                   distance_in_degree=gcarc,
                                                   phase_list=['SKKS'])
            tskks = arrivals_PHASE[0].time
            otdiff = tr.stats.starttime - otime
            tr.stats.sac['t2'] = tskks-otdiff-tr.stats.sac['b']
            tr.stats.sac['kt2'] = PHASE_CODE
            tr = tr.slice(otime+tskks-CUT_BEFORE, otime+tskks+CUT_AFTER)
            tr.write(output_file_name, format='SAC')
        else:
            """When there is only one SAC file for the station and channel,
              we will directly cut the trace according to SKKS arrival time."""
            st = read(files_for_single_channel[0])
            tr = st[0]
            otime = source_info['otime']
            evla = source_info['evla']
            evlo = source_info['evlo']
            evdp = source_info['evdp']
            stla = tr.stats.sac['stla']
            stlo = tr.stats.sac['stlo']
            gcarc = gcarc = locations2degrees(evla, evlo,
                                              stla, stlo)
            arrivals_PHASE = model.get_travel_times(source_depth_in_km=evdp,
                                                   distance_in_degree=gcarc,
                                                   phase_list=[PHASE_CODE])
            tskks = arrivals_PHASE[0].time
            otdiff = tr.stats.starttime - otime
            tr.stats.sac['t2'] = tskks-otdiff-tr.stats.sac['b']
            tr.stats.sac['kt2'] = PHASE_CODE
            tr = tr.slice(otime+tskks-CUT_BEFORE, otime+tskks+CUT_AFTER)
            tr.write(output_file_name, format='SAC')


def catalogue_avaliable_station_from_SmKS(data_directory):
    """
    This function will catalogue the available stations in the SmKS directory.
    SmKS directory are data that have been renamed and cut according to SKKS arrival time and then saved in SmKS directory.
    The nameing rule is 
        network.station.location.channel.SAC
    """

    OBJECT_DIRECTORY = "SmKS"
    df_avaliable_data = pd.DataFrame(data=np.zeros((0, 4)),
                                     columns=['network',
                                              'station',
                                              'location',
                                              'channel'])
    file_list = glob('%s/%s/*Z' % (data_directory, OBJECT_DIRECTORY))

    for file_dir in file_list:
        file_name = file_dir.split('/')[-1]
        station_info = file_name.split('.')
        network = station_info[0]
        station = station_info[1]
        channel = station_info[-1]
        if len(station_info) == 4:
            location = station_info[2]
        else:
            location = ''
        row = pd.DataFrame([{'network': network,
                             'station': station,
                             'location': location,
                             'channel': channel}])
        df_avaliable_data = pd.concat([df_avaliable_data, row],
                                      ignore_index=True)
    return df_avaliable_data


def check_cmpaz_cmpinc(file_list):
    """
    check existance and check if it need rotation.
    If it need to be rotate, copy the original to *.mis first,
    and then rotate the file.
    """

    try:
        tr0 = read(file_list[0], format='SAC')[0]
        tr1 = read(file_list[1], format='SAC')[0]
        tr2 = read(file_list[2], format='SAC')[0]
    except Exception as e:
        print(e)
        print('Cannot read data %s, %s, %s' % file_list[0],
              file_list[1], file_list[2])
        return 1
    try:
        cmpinc0 = tr0.stats.sac['cmpinc']
        cmpaz1 = tr1.stats.sac['cmpaz']
        cmpinc1 = tr1.stats.sac['cmpinc']
        cmpaz2 = tr2.stats.sac['cmpaz']
        cmpinc2 = tr2.stats.sac['cmpinc']
    
        flag = 0
        if cmpinc0 != 0:
            print('need to rotate Z, inc=%.2f' % cmpinc0)
            shutil.copy(file_list[0], '%s.mis' % file_list[0])
            flag = 1
        elif cmpinc1 != 90:
            print('need to rotate N, inc=%.2f' % cmpinc1)
            shutil.copy(file_list[1], '%s.mis' % file_list[1])
            flag = 1
        elif cmpinc2 != 90:
            print('need to rotate E, inc=%.2f' % cmpinc2)
            shutil.copy(file_list[2], '%s.mis' % file_list[2])
            flag = 1
        elif cmpaz1 != 0:
            print('need rotate N: az=%.2f' % cmpaz1)
            shutil.copy(file_list[1], '%s.mis' % file_list[1])
            flag = 1
        elif cmpaz2 != 90:
            print('need rotate E: az=%.2f' % cmpaz2)
            shutil.copy(file_list[2], '%s.mis' % file_list[2])
            flag = 1
        return flag
    except Exception as e:
        print(e)


def rotate_to_ZNE(data_directory, file_list):
    """
    This function rotate the three componets to real NEZ.
    Many stations are not aligned to the NEZ though they are nalbed as so.
    When there is an angle between the N-component and true north,
    the angle will be written in the headeras.
    """
    
    OBJECT_DIRECTORY = "SmKS"

    tr0 = read(file_list[0], format='SAC')[0]
    cmpaz0 = tr0.stats.sac['cmpaz']
    cmpinc0 = tr0.stats.sac['cmpinc']
    tr1 = read(file_list[1])[0]
    cmpaz1 = tr1.stats.sac['cmpaz']
    cmpinc1 = tr1.stats.sac['cmpinc']
    tr2 = read(file_list[2])[0]
    cmpaz2 = tr2.stats.sac['cmpaz']
    cmpinc2 = tr2.stats.sac['cmpinc']

    try:
        dataZ, dataN, dataE = rotate2zne(tr0, cmpaz0, cmpinc0-90,
                                         tr1, cmpaz1, cmpinc1-90,
                                         tr2, cmpaz2, cmpinc2-90)
        statsZ = tr0.stats
        statsZ.sac['cmpinc'] = 0
        statsZ.sac['cmpaz'] = 0
        statsN = tr1.stats
        statsN.sac['cmpinc'] = 90
        statsN.sac['cmpaz'] = 0
        statsE = tr2.stats
        statsE.sac['cmpinc'] = 90
        statsE.sac['cmpaz'] = 90
        trZ = Trace(data=dataZ, header=statsZ)
        trN = Trace(data=dataN, header=statsN)
        trE = Trace(data=dataE, header=statsE)
        file_name_Z = "%s/%s/%s.%s.%s.%s" % (data_directory,
                                            OBJECT_DIRECTORY,
                                            trZ.stats.network,
                                            trZ.stats.station,
                                            trZ.stats.location,
                                            trZ.stats.channel)
        file_name_N = "%s/%s/%s.%s.%s.%s" % (data_directory,
                                            OBJECT_DIRECTORY,
                                            trN.stats.network,
                                            trN.stats.station,
                                            trN.stats.location,
                                            trN.stats.channel)
        file_name_E = "%s/%s/%s.%s.%s.%s" % (data_directory,
                                            OBJECT_DIRECTORY,
                                            trE.stats.network,
                                            trE.stats.station,
                                            trE.stats.location,
                                            trE.stats.channel)
        trZ.write(file_name_Z, format='SAC')
        trN.write(file_name_N, format='SAC')
        trE.write(file_name_E, format='SAC')
    except Exception as e:
        print(e)


def rotate_NE_to_RT(data_directory, file_list):
    OBJECT_DIRECTORY = "SmKS"
    trN = read(file_list[1])[0]
    trE = read(file_list[2])[0]
    baz = trN.stats.sac['baz']
    band_gain = trN.stats.channel[:2]
    nptsR = trN.stats.npts
    nptsT = trE.stats.npts
    npts = min(nptsR, nptsT)
    dataR, dataT = rotate_ne_rt(trN.data[:npts], trE.data[:npts], baz)
    network = trN.stats.network
    station = trN.stats.station
    location = trN.stats.location
    channelR = '%sR' % band_gain
    channelT = '%sT' % band_gain
    trR = Trace(data=dataR[:npts], header=trN.stats)
    trT = Trace(data=dataT[:npts], header=trE.stats)
    if network == '':
        file_name_R = "%s/%s/%s.%s.%s" % (data_directory,
                                          OBJECT_DIRECTORY,
                                          network,
                                          station,
                                          location,
                                          channelR)
        file_name_T = "%s/%s/%s.%s.%s" % (data_directory,
                                          OBJECT_DIRECTORY,
                                          network,
                                          station,
                                          location,
                                          channelT)
    else:
        file_name_R = "%s/%s/%s.%s.%s.%s" % (data_directory, OBJECT_DIRECTORY,
                                            network, station, location, channelR)
        file_name_T = "%s/%s/%s.%s.%s.%s" % (data_directory, OBJECT_DIRECTORY,
                                            network, station, location, channelT)
    
    print("Write %s %s" % (file_name_R, file_name_T))
    trR.write(file_name_R, format='SAC')
    trT.write(file_name_T, format='SAC')


def rotate_all(data_directory, channel_catalog, label=0):
    """including three steps:
    1. check existance and check if it need rotation.
    2. If the alignment is not at NEZ, rotate to NEZ first.
    3. Rotate from NE to RT.
    """
    for idx, row in channel_catalog.iterrows():
        band_gain = row.channel[:2]
        if label == 0:
            file_name = '%s.%s.%s.%s' % (row.network, row.station,
                                         row.location, band_gain)
        elif label ==1:
            file_name = '%s.%s.%s' % (row.network, row.station, band_gain)
        file_name_Z = '%s/SmKS/%sZ' % (data_directory, file_name)
        file_name_N = '%s/SmKS/%sN' % (data_directory, file_name)
        file_name_E = '%s/SmKS/%sE' % (data_directory, file_name)

        if not os.path.exists(file_name_N):
            file_name_N = '%s/%s1' % (data_directory, file_name)
        if not os.path.exists(file_name_E):
            file_name_E = '%s/%s2' % (data_directory, file_name)

        if not os.path.exists(file_name_N):
            continue
        if not os.path.exists(file_name_E):
            continue

        file_list = [file_name_Z, file_name_N, file_name_E]
        # check if the station is align to the NEZ, if not, rotate to NEZ first
        result = check_cmpaz_cmpinc(file_list)
        if result == 1:
            rotate_to_ZNE(data_directory, file_list)
        # after all stations are aligned to NEZ, rotate to RT
        rotate_NE_to_RT(data_directory, file_list)


def generate_station_csv(data_directory):
    file_dir_list = glob('%s/SmKS/*R' % data_directory)
    fname_list = []
    stla_list = []
    stlo_list = []
    for file_dir in file_dir_list:
        fname = file_dir.split('/')[-1]
        print(fname)
        network = fname.split('.')[0]
        station = fname.split('.')[1]
        location = fname.split('.')[2]
        channel = fname.split('.')[-1]
        if location == channel:
            fname = '%s.%s.' % (network, station)
        else:
            fname = '%s.%s.%s' % (network, station, location)
        #fname = fname.replace('.%s' % channel, '')
        try:
            tr = read(file_dir)[0]
            stla = tr.stats.sac['stla']
            stlo = tr.stats.sac['stlo']
            fname_list.append(fname)
            stla_list.append(stla)
            stlo_list.append(stlo)
        except Exception as e:
            print(e)
    df_station = pd.DataFrame({'name': fname_list,
                               'stla': stla_list,
                               'stlo': stlo_list})
    df_station.to_csv('%s/stations.csv' % data_directory)


def generate_station_list_for_AxiSEM3D(data_directory):
    file_dir_list = glob('%s/SmKS/*R' % data_directory)
    with open('%s/axisem3d_station_list.txt' % data_directory, 'w') as fp:
        for file_dir in file_dir_list:
            fname = file_dir.split('/')[-1]
            station_info = fname.split('.')
            network = station_info[0]
            station = station_info[1]
            location = station_info[2]
            if location != 'BHR':
                station_location = '%s.%s' % (station, location)
            else:
                station_location = '%s.' % station
            try:
                tr = read(file_dir)[0]
                stla = tr.stats.sac['stla']
                stlo = tr.stats.sac['stlo']
                stel = tr.stats.sac['stel']
                fp.write('%-8s\t%s\t%-9s\t%-9s\t%-9s\t0.00\n' % (
                          station_location, network, stla, stlo, stel))
            except Exception as e:
                print(e)
    fp.close()


def generate_station_list_for_DSM(data_directory):
    file_dir_list = glob('%s/SmKS/*R' % data_directory)
    with open('%s/dsm_station_list.txt' % data_directory, 'w') as fp1, \
        open('%s/dsm_output_files_SH.txt' % data_directory, 'w') as fp2, \
            open('%s/dsm_output_files_PSV.txt' % data_directory, 'w') as fp3:

        for file_dir in file_dir_list:
            fname = file_dir.split('/')[-1]
            station_info = fname.split('.')
            network = station_info[0]
            station = station_info[1]
            location = station_info[2]
            if location != 'BHR':
                station_location = '%s.%s' % (station, location)
            else:
                station_location = '%s.' % station
            try:
                tr = read(file_dir)[0]
                stla = tr.stats.sac['stla']
                stlo = tr.stats.sac['stlo']
                fp1.write('%-9s\t%-9s\tlat, lon (deg)\n' % (stla, stlo))
                fp2.write('output/%s.%s.SH.spc\n' % (network,
                                                     station_location))
                fp3.write('output/%s.%s.PSV.spc\n' % (network,
                                                      station_location))
            except Exception as e:
                print(e)
    fp1.close()
    fp2.close()
    fp3.close()


def standardize_raw_data_from_wilber(event_directory):
    """This function will standardize the raw data from IRIS Wilber3.
    It will catalogue all raw SAC fines in SAC directory,
    and then cut the data according to SKKS arrival time,
    and save the cut data in SmKS directory."""
    source_info = read_hypo('%s/hypo.csv' % event_directory)
    print("read hypo file successfully!")
    channel_catalog = catalogue_raw_channel_from_Wilber(event_directory)
    print("check the available channels successfully!")
    standerdize_every_station(event_directory, channel_catalog, source_info)
    print("standardize data and save to /SmKS successfully!")


def rotate_SmKS_data_from_NE_to_RT(event_directory):
    """This function will rotate the data in SmKS directory from NE to RT."""
    channel_catalog = catalogue_avaliable_station_from_SmKS(event_directory)
    rotate_all(event_directory, channel_catalog, 0)
    print("Rotate data from NE to RT successfully!")


def obs_traces_to_matrix(directory, component, sample_rate, trace_length):
    file_list = glob(directory+'/SmKS/*.??'+component)
    print(file_list)
    file_number = len(file_list)
    npts = sample_rate * trace_length
    data_matrix = np.zeros((npts, file_number))
    name_list = []
    stla_list = []
    stlo_list = []
    for i in tqdm(np.arange(file_number)):
        file_dir = file_list[i]
        file_name = file_dir.split('/')[-1]
        network = file_name.split('.')[0]
        station = file_name.split('.')[1]
        location = file_name.split('.')[2]
        channel = file_name.split('.')[-1]
        try:
            st = read(file_dir)
            st.resample(sample_rate)
            tr = st[0]
            if location == channel:
                name_list.append('%s.%s.' % (network, station))
            else:
                name_list.append('%s.%s.%s' % (network, station, location))
            # name_list.append('%s.%s.%s' % (network, station, location))
            stla_list.append(tr.stats.sac['stla'])
            stlo_list.append(tr.stats.sac['stlo'])
            data = bandpass(tr.data, 0.02, 0.2, sample_rate, 4, zerophase=True)
            len_data = len(data)
            if len_data >= npts:
                data_matrix[:, i] = data[:npts]/np.max(np.abs(data))
            else:
                data_matrix[:len_data, i] = data/np.max(np.abs(data))
        except Exception as e:
            print(e)
    df_station = pd.DataFrame({'station': name_list,
                               'stla': stla_list,
                               'stlo': stlo_list})
    data_matrix = data_matrix[~np.all(data_matrix == 0, axis=1)]
    return data_matrix, df_station


def prepare_obs_data(directory, component, sample_rate, trace_length,
                      half_window, before_pick, after_pick):

    hypo_dir = '%s/hypo.csv' % directory
    df_hypo = pd.read_csv(hypo_dir)
    print('... Convert data files to raw matrix and generate info file ...')
    raw_matrix, df_station = obs_traces_to_matrix(directory=directory,
                                                    component=component,
                                                    sample_rate=sample_rate,
                                                    trace_length=trace_length)
    print('... Calculate distance and time ...')
    df_station = cal_dist_time(df_station, df_hypo)

    signal_begin = np.ones(len(df_station))*100
    print('... Align the traces ... ')
    data_matrix, signal_matrix = matrix_align_slant(data_matrix=raw_matrix,
                                                    sample_rate=sample_rate,
                                                    signal_begin=signal_begin,
                                                    half_window=half_window,
                                                    before_pick=before_pick,
                                                    after_pick=after_pick)
    plot_eq_map(df_station, df_hypo)
    plot_data_matrix(data_matrix, df_station, sample_rate)
    np.save('%s/np_waveforms_obs.npy' % directory, data_matrix)
    df_station['tridx'] = np.arange(len(df_station))
    df_station.to_csv('%s/df_stations_obs.csv' % directory,
                      index=False, float_format='%.3f')
    generate_station_csv(directory)
    generate_station_list_for_AxiSEM3D(directory)
    generate_station_list_for_DSM(directory)


# 1
# event_directory = '../Data/2003-05-26-mw68-mindanao-philippines'
# 2
# event_directory = '../Data/2005-03-21-mw68-salta-province-argentina-1'
# 3
# event_directory = '../Data/2007-10-16-mw66-south-of-fiji-islands-1'
# 4
# event_directory = '../Data/2010-07-24-mw66-mindanao-philippines'
# 5
# event_directory = '../Data/2010-07-29-mw66-mindanao-philippines-1'
# 6
# event_directory = '../Data/2011-01-01-mw70-santiago-del-estero-prov-arg'
# 7
# event_directory = '../Data/2011-07-29-mw67-south-of-fiji-islands-2'
# 8
# event_directory = '../Data/2011-11-22-mw66-central-bolivia-6'
# 9
# event_directory = '../Data/2013-05-14-mw68-mariana-islands'
# 10
# event_directory = '../Data/2013-05-24-mw67-sea-of-okhotsk'
# 11
# event_directory = '../Data/2013-10-01-mw67-sea-of-okhotsk'
# 12
# event_directory = '../Data/2014-05-04-mw66-south-of-fiji-islands-1'
# 13
# event_directory = '../Data/2020-07-06-mww67-java-sea'
# 14
# event_directory = '../Data/2021-10-09-mww69-vanuatu-islands-region'
# 15
# event_directory = '../Data/2023-03-01-mww66-bismarck-sea'






