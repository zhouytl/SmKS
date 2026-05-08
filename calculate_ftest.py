#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 14:06:52 2026

@author: zhouyangtianli
"""

import numpy as np
import pandas as pd


def ftest(data1, data2):

    N = len(data1)
    B = 1000  # number of bootstrap samples
    
    delta = []
    
    for _ in range(B):
        # sample indices with replacement
        idx = np.random.choice(N, size=N, replace=True)
        
        # compute RSS for this bootstrap sample
        rss1 = np.sum(data1[idx]**2)
        rss2 = np.sum(data2[idx]**2)
        
        delta.append(rss1 - rss2)
    
    delta = np.array(delta)
    
    # Results
    mean_delta = np.mean(delta)
    ci_lower = np.percentile(delta, 25)
    ci_upper = np.percentile(delta, 75)
    prob_B_better = np.mean(delta > 0)
    
    print("Mean ΔRSS:", mean_delta)
    print("50% CI:", [ci_lower, ci_upper])
    print("P(Model 2 better):", prob_B_better)
    
df0 = pd.read_csv('../Data/df_all_groups.csv')
df1 = pd.read_csv('../Data/df_all_groups_b.csv')
df2 = pd.read_csv('../Data/df_all_groups_c.csv')
df3 = pd.read_csv('../Data/df_all_groups_a.csv')

# ftest(df0.residualp, df0.residual1)
# ftest(df0.residual1, df0.residual3)

# ftest(df1.residual3, df1.residualc)
# ftest(df2.residual3, df2.residualc)

ftest(df1.residuals, df2.residuals)
    