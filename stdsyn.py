#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zhouyangtianli, 2026-04-26

"""

import os
from glob import glob
import netCDF4
import numpy as np
import pandas as pd
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
from obspy.core import Trace, UTCDateTime, Stats
import subprocess
from obspy import read
from obspy.signal.filter import bandpass
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from cartopy import crs as ccrs
from glob import glob
from tqdm import tqdm

from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees
from obspy.imaging.beachball import beach


import pyproj
from raypath_utils import cal_raypath, cal_dist_time
from visualization_utils import plot_eq_map, plot_data_matrix
from data_utils import matrix_align_slant

projection = pyproj.Geod(ellps='WGS84')
model_prem = TauPyModel(model="prem")


def convert_evtdata_ascii2sac(odir, dc_event, df_stations):

    model = TauPyModel(model='ak135')
    os.makedirs(odir + '/sac', exist_ok=True)
    data_time = np.loadtxt(odir + '/data_time.ascii')
    for idx, row in df_stations.iterrows():
        print(row)
        fname = row['name']
        try:
            waveform = np.loadtxt(odir + '/%s.ascii' % fname)
        except Exception as e:
            print(e)
            continue

        stats = Stats()
        stats.starttime = UTCDateTime(data_time[0])
        stats.delta = UTCDateTime(data_time[1] - data_time[0])
        stats.npts = len(data_time)
        gcarc = locations2degrees(dc_event['evla'], dc_event['evlo'],
                                  row.stla, row.stlo)

        arrivals_Pdiff = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['Pdiff'])

        arrivals_PKP = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PKP'])

        arrivals_PP = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PP'])

        arrivals_PPP = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PPP'])

        arrivals_SKKS = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['SKKS'])

        arrivals_PPS = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PPS'])

        arrivals_PPPS = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['Sdiff'])


        # sac header
        sac_header = {}
        sac_header['evla'] = dc_event['evla']
        sac_header['evlo'] = dc_event['evlo']
        sac_header['evdp'] = dc_event['evdp']
        sac_header['kstnm'] = fname.split('.')[1]
        sac_header['knetwk'] = fname.split('.')[0]
        sac_header['stla'] = row['stla']
        sac_header['stlo'] = row['stlo']
        sac_header['stdp'] = 0.0
        sac_header['gcarc'] = gcarc

        if len(arrivals_Pdiff) > 0:
            sac_header['kt0'] = 'Pdiff'
            sac_header['t0'] = arrivals_Pdiff[0].time
        if len(arrivals_PKP) > 0:
            sac_header['kt1'] = 'PKP'
            sac_header['t1'] = arrivals_PKP[0].time
        if len(arrivals_PP) > 0:
            sac_header['kt2'] = 'PP'
            sac_header['t2'] = arrivals_PP[0].time
        if len(arrivals_PPP) > 0:
            sac_header['kt3'] = 'PPP'
            sac_header['t3'] = arrivals_PPP[0].time
        if len(arrivals_SKKS) > 0:
            sac_header['kt4'] = 'SKKS'
            sac_header['t4'] = arrivals_SKKS[0].time
        if len(arrivals_PPS) > 0:
            sac_header['kt5'] = 'PPS'
            sac_header['t5'] = arrivals_PPS[0].time
        if len(arrivals_PPPS) > 0:
            sac_header['kt6'] = 'Sdiff'
            sac_header['t6'] = arrivals_PPPS[0].time

        # loop over channels
        for ich, ch in enumerate('RTZ'):
            # sac header
            sac_header['kcmpnm'] = ch
            stats.sac = sac_header
            # create and process trace
            tr = Trace(data=waveform[:, ich], header=stats)
            tr.resample(10.)
            tr = tr.slice(UTCDateTime(0.), UTCDateTime(3000.))
            tr.write('%s/sac/%s.%s' % (odir, fname, ch), format='SAC')
            print('%s.%s converted' % (fname, ch))


def convert_evtdata_nc2sac(odir, dc_event, df_stations,
                           nc_data, nc_info, nc_rank):

    model = TauPyModel(model='ak135')

    os.makedirs(odir + '/sac', exist_ok=True)
    data_time = nc_data['data_time'][:]
    data_wave = nc_data['data_wave']
    nc_info = nc_info[nc_info.MPI_RANK == nc_rank]
    for idx, row in nc_info.iterrows():
        fname = row.STATION_KEY
        tridx = row.STATION_INDEX_IN_RANK
        waveform = data_wave[tridx, :, :]
        sta_info = df_stations[df_stations.name == fname]
        if len(sta_info) == 0:
            continue
        stats = Stats()
        stats.starttime = UTCDateTime(data_time[0])
        stats.delta = UTCDateTime(data_time[1] - data_time[0])
        stats.npts = len(data_time)
        gcarc = locations2degrees(dc_event['evla'], dc_event['evlo'],
                                  sta_info.stla, sta_info.stlo)

        arrivals_Pdiff = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['Pdiff'])

        arrivals_PKP = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PKP'])

        arrivals_PP = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PP'])

        arrivals_PPP = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PPP'])

        arrivals_SKKS = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['SKKS'])

        arrivals_PPS = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PPS'])

        arrivals_PPPS = model.get_travel_times(
            source_depth_in_km=dc_event['evdp'],
            distance_in_degree=gcarc,
            phase_list=['PPPS'])

        # sac header
        sac_header = {}
        sac_header['evla'] = dc_event['evla']
        sac_header['evlo'] = dc_event['evlo']
        sac_header['evdp'] = dc_event['evdp']
        sac_header['kstnm'] = fname.split('.')[1]
        sac_header['knetwk'] = fname.split('.')[0]
        sac_header['stla'] = sta_info['stla']
        sac_header['stlo'] = sta_info['stlo']
        sac_header['stdp'] = 0.0
        sac_header['gcarc'] = gcarc

        if len(arrivals_Pdiff) > 0:
            sac_header['kt0'] = 'Pdiff'
            sac_header['t0'] = arrivals_Pdiff[0].time
        if len(arrivals_PKP) > 0:
            sac_header['kt1'] = 'PKP'
            sac_header['t1'] = arrivals_PKP[0].time
        if len(arrivals_PP) > 0:
            sac_header['kt2'] = 'PP'
            sac_header['t2'] = arrivals_PP[0].time
        if len(arrivals_PPP) > 0:
            sac_header['kt3'] = 'PPP'
            sac_header['t3'] = arrivals_PPP[0].time
        if len(arrivals_SKKS) > 0:
            sac_header['kt4'] = 'SKKS'
            sac_header['t4'] = arrivals_SKKS[0].time
        if len(arrivals_PPS) > 0:
            sac_header['kt5'] = 'PPS'
            sac_header['t5'] = arrivals_PPS[0].time
        if len(arrivals_PPPS) > 0:
            sac_header['kt6'] = 'PPPS'
            sac_header['t6'] = arrivals_PPPS[0].time

        # loop over channels
        for ich, ch in enumerate('RTZ'):
            # sac header
            sac_header['kcmpnm'] = ch
            stats.sac = sac_header
            # create and process trace
            tr = Trace(data=waveform[ich, :], header=stats)
            tr.resample(10.)
            tr = tr.slice(UTCDateTime(0.), UTCDateTime(3000.))
            tr.write('%s/sac/%s.%s' % (odir, fname, ch), format='SAC')
            print('%s.%s converted' % (fname, ch))


def convert_simudata(event_directory, label):
    # label = 'simu3Da'
    df_stations = pd.read_csv('%s/stations.csv' % event_directory)
    hypo = pd.read_csv('%s/hypo.csv' % event_directory)
    simu_dir = '%s/%s/output/stations/IRIS' % (event_directory, label)
    data_info = pd.read_csv('%s/rank_station.info' % simu_dir, sep=' ')

    dc_evt = {'evla': hypo.evla[0], 'evlo': hypo.evlo[0], 'evdp': hypo.evdp[0]}

    ncfile_list = glob('%s/axisem3d_synthetics.nc.rank*' % simu_dir)
    for dir_nc in ncfile_list:
        fname_nc = dir_nc.split('/')[-1]
        rank = int(fname_nc.replace("axisem3d_synthetics.nc.rank", ""))
        data_nc = netCDF4.Dataset(dir_nc)
        convert_evtdata_nc2sac(odir=simu_dir,
                                dc_event=dc_evt,
                                df_stations=df_stations,
                                nc_data=data_nc,
                                nc_info=data_info,
                                nc_rank=rank)


def syn_traces_to_matrix(directory, component, sample_rate, trace_length):
    '''
    need to change the file name when convert dsm and axisem3d
    dsm file end with Rs, while axisem3d file only end with R
    '''

    file_list = glob(directory+'/*.%s' % component)
    file_number = len(file_list)
    npts = sample_rate * trace_length
    data_matrix = np.zeros((npts, file_number))
    station_info = np.zeros((2, file_number))
    name_list = []
    for i in tqdm(np.arange(file_number)):
        file_dir = file_list[i]
        file_name = file_dir.split('/')[-1]
        network = file_name.split('.')[0]
        station = file_name.split('.')[1]
        location = file_name.split('.')[2]
        channel = file_name.split('.')[-1]
        st = read(file_dir)
        st.resample(sample_rate)
        tr = st[0]
        station_info[:, i] = np.array([tr.stats.sac['stla'],
                                       tr.stats.sac['stlo']])
        if location == channel:
            name_list.append('%s.%s.' % (network, station))
        else:
            name_list.append('%s.%s.%s' % (network, station, location))
        data = bandpass(tr.data, 0.02, 0.2, sample_rate, 4, zerophase=True)
        len_data = len(data)
        if len_data >= npts:
            data_matrix[:, i] = data[:npts]/np.max(data)
        else:
            data_matrix[:len_data, i] = data/np.max(data)
    df_station = pd.DataFrame({'station': name_list,
                               'stla': station_info[0, :],
                               'stlo': station_info[1, :]})
    return data_matrix, df_station



def prepare_syn_data(directory, component, sample_rate, trace_length,
                      half_window, before_pick, after_pick, label):

    sac_directory = '%s/%s/output/stations/IRIS/sac' % (directory, label)
    hypo_dir = '%s/hypo.csv' % directory
    df_hypo = pd.read_csv(hypo_dir)
    print('... Convert data files to raw matrix and generate info file ...')
    raw_matrix, df_station = syn_traces_to_matrix(directory=sac_directory,
                                                    component=component,
                                                    sample_rate=sample_rate,
                                                    trace_length=trace_length)
    print('... Calculate distance and time ...')
    df_station = cal_dist_time(df_station, df_hypo)
    signal_begin = df_station.s2ks.values
    print('... Align the traces ... ')
    data_matrix, signal_matrix = matrix_align_slant(data_matrix=raw_matrix,
                                                    sample_rate=sample_rate,
                                                    signal_begin=signal_begin,
                                                    half_window=half_window,
                                                    before_pick=before_pick,
                                                    after_pick=after_pick)
    plot_eq_map(df_station, df_hypo)
    plot_data_matrix(data_matrix, df_station, sample_rate)
    np.save('%s/np_waveforms_%s.npy' % (directory, label), data_matrix)
    df_station['tridx'] = np.arange(len(df_station))
    df_station.to_csv('%s/df_stations_%s.csv' % (directory, label),
                      index=False, float_format='%.3f')
    
