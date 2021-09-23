#!python
# -*- coding: utf-8 -*-
# @author: Kun

'''
Author: Kun
Date: 2021-09-22 09:38:19
LastEditTime: 2021-09-23 14:02:21
LastEditors: Kun
Description: 
FilePath: /ThreatReportExtractor/project_config.py
'''

import os

PROJECT_HOME = os.path.abspath(os.getcwd())  # current home dir


######################################################################################

DATA_DIR_PATH = os.path.join(PROJECT_HOME, "data")

RE_PATTERNS_FILE_PATH = os.path.join(DATA_DIR_PATH, "patterns.ini")

SEC_PATTERNS_FILE_PATH = os.path.join(DATA_DIR_PATH, "lists.ini")

######################################################################################
