#!python
# -*- coding: utf-8 -*-
# @author: Kun

'''
Author: Kun
Date: 2021-09-23 13:43:49
LastEditTime: 2021-09-23 14:09:10
LastEditors: Kun
Description: 
FilePath: /ThreatReportExtractor/data_loader/pattern_loader.py
'''

import re
import configparser as ConfigParser


def load_patterns(path):

    patterns = {}

    # path = "./data/patterns.ini"

    config = ConfigParser.ConfigParser()
    with open(path) as f:
        config.readfp(f)
    for ind_type in config.sections():
        try:
            ind_pattern = config.get(ind_type, 'pattern')
        except:
            continue
        if ind_pattern:
            ind_regex = re.compile(ind_pattern, re.IGNORECASE | re.M)
            patterns[ind_type] = ind_regex
    return patterns


def load_lists(fpath):
    patterns = {}

    # fpath = "./data/lists.ini"

    config = ConfigParser.ConfigParser()
    with open(fpath) as f:
        config.readfp(f)
    for ind_type in config.sections():
        try:
            ind_pattern = config.get(ind_type, 'pattern')
        except:
            continue
        if ind_pattern:
            patterns[ind_type] = ind_pattern
    return patterns
