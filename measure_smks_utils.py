#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zhouyangtianli 
"""

import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
from scipy.signal import correlate, hilbert, find_peaks, windows
from visualization_utils import plot_data_matrix

# def plot_data_matrix(data_matrix, df_station, sample_rate):
#     M, N = data_matrix.shape
#     time = np.arange(1, M+1)/sample_rate
#     gcarc = df_station.gcarc.values
#     fig = plt.figure(figsize=(1, 8))
#     ax = fig.add_subplot(111)
#     for i in np.arange(N):
#         ax.plot(time, gcarc[i]+2*data_matrix[:, i], 'g', linewidth=0.2)
#     plt.show()


def cut_signal(data_matrix, sample_rate, signal_peak, half_window):
    (M, N) = data_matrix.shape
    signal_matrix = np.zeros((int(2*half_window*sample_rate), N))
    for i in np.arange(N):
        idx1 = int(signal_peak[i]*sample_rate) - int(half_window*sample_rate)
        idx2 = int(signal_peak[i]*sample_rate) + int(half_window*sample_rate)
        signal_matrix[:, i] = data_matrix[idx1: idx2, i]
    return signal_matrix


def cal_corr(sig1, sig2, sample_rate):
    npts = len(sig1) + len(sig2)
    time = np.arange(npts) / sample_rate
    fcorr = correlate(sig2, sig1, 'full', 'fft')
    pow_sig1 = np.sum(sig1 ** 2)
    pow_sig2 = np.sum(sig2 ** 2)
    weight = np.sqrt(pow_sig1 * np.max(pow_sig2))
    ccf_np = fcorr / weight
    maximum_idx = np.argmax(np.abs(ccf_np))
    tdiff = time[maximum_idx] - npts/sample_rate/2
    coef = ccf_np[maximum_idx]
    if ccf_np[maximum_idx] < 0:
        flag = -1
    else:
        flag = 1
    return tdiff, coef, flag


def cal_coef(sig1, sig2, sample_rate):
    coef = correlate(sig1, sig2, 'valid', 'fft')[0]
    pow_sig1 = np.sum(sig1 ** 2)
    pow_sig2 = np.sum(sig2 ** 2)
    weight = np.sqrt(pow_sig1 * np.max(pow_sig2))
    coef = coef / weight
    return coef


def measure_residual_solo(directory, label, sample_rate, before_pick,
                        sign_window, corr_window, peak_window,
                        layer: int = 0):

    df_station = pd.read_csv('%s/df_stations_%s.csv' % (directory, label))
    data_matrix = np.load('%s/np_waveforms_%s.npy' % (directory, label))
    data_matrix = data_matrix[:, :, layer]
    M, N = data_matrix.shape
    data_matrix_ht = np.imag(hilbert(data_matrix, axis=0))
    t32 = df_station.s3ks.values - df_station.s2ks.values
    s2ks_arrivals = before_pick + np.zeros(N)
    s3ks_arrivals = before_pick + t32
    #  pick peaks as S3KS arrival time, Hibert[S3KS]
    #  peak window should be smaller than the signal wavelength
    #  pick at the peak instead of maximum
    s3ks_waveform_for_picking = cut_signal(data_matrix=data_matrix_ht,
                                           sample_rate=sample_rate,
                                           signal_peak=s3ks_arrivals,
                                           half_window=peak_window)
    tdiff_pp = np.zeros(N)
    for i in np.arange(N):
        s3ks_row = s3ks_waveform_for_picking[:, i] * \
            windows.tukey(int(2*peak_window)*sample_rate)
        peaks_idx, _ = find_peaks(np.abs(s3ks_row))
        if len(peaks_idx) == 0:
            peaks_idx = [0]
        peaks_values = s3ks_row[peaks_idx]
        max_peaks_idx = np.argmax(np.abs(peaks_values))
        tdiff = peaks_idx[max_peaks_idx]/sample_rate - peak_window
        tdiff_pp[i] = tdiff
    # exit()
    s3ks_template_ht = cut_signal(data_matrix=data_matrix_ht,
                                  sample_rate=sample_rate,
                                  signal_peak=s3ks_arrivals+tdiff_pp,
                                  half_window=sign_window)
    #  the S2KS template are sliced without Hilbert transform
    #  for calculate SNR and ccoef between the picked S3KS
    #  the ccoef will be calculated in the loop
    s2ks_template = cut_signal(data_matrix=data_matrix,
                               sample_rate=sample_rate,
                               signal_peak=s2ks_arrivals,
                               half_window=sign_window)
    s3ks_template = cut_signal(data_matrix=data_matrix,
                               sample_rate=sample_rate,
                               signal_peak=s3ks_arrivals+tdiff_pp,
                               half_window=sign_window)
    
    
    noise_template = cut_signal(data_matrix=data_matrix,
                                sample_rate=sample_rate,
                                signal_peak=s2ks_arrivals-3*sign_window,
                                half_window=sign_window)
    #  calculate SNR
    pow_s2ks = np.sum(s2ks_template ** 2, axis=0)
    pow_noise = np.sum(noise_template ** 2, axis=0)
    snr = np.sqrt(pow_s2ks/pow_noise)
    #  calculate the tdiff by cross correlation
    #  the waveform window including S3KS for mathcing should be longer
    s2ks_template_ht = cut_signal(data_matrix=data_matrix_ht,
                                  sample_rate=sample_rate,
                                  signal_peak=s2ks_arrivals,
                                  half_window=sign_window)
    s3ks_waveform_for_matching = cut_signal(data_matrix=data_matrix,
                                            sample_rate=sample_rate,
                                            signal_peak=s3ks_arrivals,
                                            half_window=corr_window)
    ccoef_cc_list = []
    tdiff_cc_list = []
    ccoef_pp_list = []
    for i in tqdm(np.arange(N)):
        ccoef_pp = cal_coef(-s3ks_template_ht[:, i],
                            s2ks_template[:, i], sample_rate)
        window_length = 2*sign_window*sample_rate
        time_window = np.arange(window_length) / sample_rate - sign_window
        time = np.arange(M)/sample_rate - before_pick
        tdiff_cc, ccoef_cc, flag = cal_corr(s2ks_template_ht[:, i],
                                            s3ks_waveform_for_matching[:, i],
                                            sample_rate)
        #  for plotting
        fig = plt.figure(num=None, figsize=(8, 2), dpi=600, edgecolor='k')
        ftsz = 10
        ax_waveform = fig.add_subplot(111)
        #  calculate fitting amplitude
        s3ks_max = np.max(np.abs(s3ks_waveform_for_matching[:, i]))
        s2ks_max = np.max(np.abs(s2ks_template_ht[:, i]))
        data_matrix_max = np.max(np.abs(data_matrix[:, i]))
        data_matrix_ht_max = np.max(np.abs(data_matrix_ht[:, i]))
        fit_amp = flag * s3ks_max / s2ks_max / s2ks_max
        #  plot waveforms
        ax_waveform.plot(time,
                         data_matrix[:, i] / data_matrix_max,
                         'k', label='original signal')
        ax_waveform.plot(time,
                         data_matrix_ht[:, i]/data_matrix_ht_max,
                         ':k', label='hilbert transform')
        ax_waveform.plot(t32[i]+tdiff_cc+time_window,
                         fit_amp*s2ks_template_ht[:, i],
                         'r', label='S2KS template')
        #  plot picks
        ax_waveform.plot([0, 0], [-1.0, 1.5], 'b')
        ax_waveform.plot([t32[i], t32[i]], [-1.0, 1.5], 'b',
                         label='prediction')
        ax_waveform.plot([t32[i]+tdiff_pp[i], t32[i]+tdiff_pp[i]],
                         [-1.0, 1.5], ':b', label='pick')
        #  plot windows
        ax_waveform.fill_betweenx([-1.0, 1.5],
                                  -sign_window, +sign_window,
                                  facecolor='m', alpha=0.2)
        ax_waveform.fill_betweenx([-1.0, 1.5],
                                  t32[i]-corr_window, t32[i]+corr_window,
                                  facecolor='c', alpha=0.2)
        ax_waveform.fill_betweenx([-1.0, 1.5],
                                  -4*sign_window,
                                  -2*sign_window,
                                  facecolor='k', alpha=0.1)
        #  label SNR
        ax_waveform.text(-before_pick, 1.2,
                         '  SNR=%.2f' % snr[i], fontsize=ftsz)
        ax_waveform.text(-before_pick, 0.9,
                         '  dt(cc) = %.2f' % tdiff_cc, fontsize=ftsz)
        ax_waveform.text(-before_pick, 0.6,
                         '  dt(pp) = %.2f' % tdiff_pp[i], fontsize=ftsz)
        ax_waveform.set_xlim([-before_pick, M/sample_rate-before_pick])
        ax_waveform.set_ylim([-1.0, 1.5])
        ax_waveform.legend(loc='upper right', fontsize=ftsz)
        ax_waveform.set_title('%s, gcarc=%.2f' % (df_station.loc[i, 'station'],
                                                  df_station.loc[i, 'gcarc']))
        ax_waveform.set_xlabel('Time (s)')
        ax_waveform.set_ylabel('Amplitude')
        output_directory = '%s/Figures/individual_%d' % (directory, layer)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)
        fig.savefig('%s/%s.png' % (output_directory,
                                   df_station.loc[i, 'station']))
        plt.close()
        ccoef_cc_list.append(ccoef_cc)
        tdiff_cc_list.append(tdiff_cc)
        ccoef_pp_list.append(ccoef_pp)
    df_station['t32_cc'] = tdiff_cc_list
    df_station['t32_pp'] = tdiff_pp
    df_station['ccf_cc'] = ccoef_cc_list
    df_station['ccf_pp'] = ccoef_pp_list
    df_station['snr'] = snr
    df_station.to_csv('%s/df_measure_individual_%d.csv' % (directory, layer),
                      index=False, float_format='%.3f')


# def plot_data_matrix(data_matrix, df_station, sample_rate):
#     M, N = data_matrix.shape
#     time = np.arange(1, M+1)/sample_rate
#     gcarc = df_station.gcarc.values
#     fig = plt.figure(figsize=(1, 8))
#     ax = fig.add_subplot(111)
#     for i in np.arange(N):
#         ax.plot(time, gcarc[i]+2*data_matrix[:, i], 'g', linewidth=0.2)
#     plt.show()


# def cut_signal(data_matrix, sample_rate, signal_peak, half_window):
#     (M, N) = data_matrix.shape
#     signal_matrix = np.zeros((int(2*half_window*sample_rate), N))
#     for i in np.arange(N):
#         idx1 = int(signal_peak[i]*sample_rate) - int(half_window*sample_rate)
#         idx2 = int(signal_peak[i]*sample_rate) + int(half_window*sample_rate)
#         signal_matrix[:, i] = data_matrix[idx1: idx2, i]
#     return signal_matrix


# def cal_corr(sig1, sig2, sample_rate):
#     npts = len(sig1) + len(sig2)
#     time = np.arange(npts) / sample_rate
#     fcorr = correlate(sig1, sig2, 'full', 'fft')
#     pow_sig1 = np.sum(sig1 ** 2)
#     pow_sig2 = np.sum(sig2 ** 2)
#     weight = np.sqrt(pow_sig1 * np.max(pow_sig2))
#     ccf_np = fcorr / weight
#     maximum_idx = np.argmax(ccf_np)
#     tdiff = time[maximum_idx] - npts/sample_rate/2
#     coef = ccf_np[maximum_idx]
#     return tdiff, coef


def measure_residual_pair(directory, mtype, label, layer,
                        sample_rate, before_pick,
                        corr_window):
    data_matrix = '%s/np_waveforms_%s%s.npy' % (directory, mtype, label)
    df_station = '%s/df_stations_%s%s.csv' % (directory, mtype, label)

    df_station = pd.read_csv(df_station)
    data_matrix = np.load(data_matrix)
    M, N, _ = data_matrix.shape

    t32 = df_station.s3ks.values - df_station.s2ks.values
    s3ks_arrivals = before_pick + t32
    s3ks_waveform_1 = cut_signal(data_matrix=data_matrix[:, :, layer],
                                 sample_rate=sample_rate,
                                 signal_peak=s3ks_arrivals,
                                 half_window=corr_window)
    s3ks_waveform_2 = cut_signal(data_matrix=data_matrix[:, :, 0],
                                 sample_rate=sample_rate,
                                 signal_peak=s3ks_arrivals,
                                 half_window=corr_window)
    ccoef_cc_list = []
    tdiff_cc_list = []
    for i in tqdm(np.arange(N)):
        window_length = 2*corr_window*sample_rate
        time_window = np.arange(window_length) / sample_rate - corr_window
        time = np.arange(M)/sample_rate - before_pick
        tdiff_cc, ccoef_cc, flag = cal_corr(s3ks_waveform_2[:, i],
                                        s3ks_waveform_1[:, i],
                                        sample_rate)
        waveform_max_1 = np.max(np.abs(data_matrix[:, i, layer]))
        waveform_max_2 = np.max(np.abs(data_matrix[:, i, 0]))
        s3ks_max_1 = np.max(np.abs(s3ks_waveform_1[:, i]))
        s3ks_max_2 = np.max(np.abs(s3ks_waveform_2[:, i]))
        fit_amp = s3ks_max_2 / waveform_max_2 / s3ks_max_1
        #  for plotting
        fig = plt.figure(num=None, figsize=(8, 2), dpi=600, edgecolor='k')
        ftsz = 10
        ax_waveform = fig.add_subplot(111)
        #  calculate fitting amplitude
        #  plot waveforms
        ax_waveform.plot(time,
                         data_matrix[:, i, layer] /
                         np.max(data_matrix[:, i, layer]),
                         'k', linewidth=2, label='Simulated')
        ax_waveform.plot(time,
                         data_matrix[:, i, 0] /
                         np.max(data_matrix[:, i, 0]),
                         'b', linewidth=2, label='observed')
        ax_waveform.plot(t32[i]+tdiff_cc+time_window,
                         fit_amp*s3ks_waveform_1[:, i],
                         'r', linewidth=1.5, label='Fitted')
        #  plot picks
        ax_waveform.plot([0, 0], [-1.0, 1.5], 'm')
        ax_waveform.plot([t32[i], t32[i]], [-1.0, 1.5], 'm',
                         label='TauP prediction')
        #  plot windows
        ax_waveform.fill_betweenx([-1.0, 1.5],
                                  t32[i]-corr_window, t32[i]+corr_window,
                                  facecolor='c', alpha=0.2)

        #  label SNR
        ax_waveform.text(-before_pick, 0.9,
                         '  dt = %.2f' % tdiff_cc, fontsize=ftsz)
        ax_waveform.text(-before_pick, 1.2,
                         '  cc = %.2f' % ccoef_cc, fontsize=ftsz)
        ax_waveform.set_xlim([-before_pick, M/sample_rate-before_pick])
        ax_waveform.set_ylim([-1.0, 1.5])
        ax_waveform.legend(loc='upper right', fontsize=ftsz)
        ax_waveform.set_title('%s, gcarc=%.2f' % (df_station.loc[i, 'station'],
                                                  df_station.loc[i, 'gcarc']))
        ax_waveform.set_xlabel('Time (s)')
        ax_waveform.set_ylabel('Amplitude')
        # plt.show()
        output_directory = '%s/Figures/synchronized_%s_%s' % (directory, layer, label)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        fig.savefig('%s/%s.png' % (output_directory,
                                   df_station.loc[i, 'station']))
        plt.close()
        ccoef_cc_list.append(ccoef_cc)
        tdiff_cc_list.append(tdiff_cc)
    df_station['t32_fw'] = tdiff_cc_list
    df_station['ccf_fw'] = ccoef_cc_list
    df_station.to_csv('%s/df_measure_synchronized_%s_%s.csv' % (directory, layer, label),
                      index=False, float_format='%.3f')



