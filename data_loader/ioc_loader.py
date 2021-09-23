#!python
# -*- coding: utf-8 -*-
# @author: Kun

'''
Author: Kun
Date: 2021-09-23 14:31:27
LastEditTime: 2021-09-23 14:31:27
LastEditors: Kun
Description: 
FilePath: /ThreatReportExtractor/data_loader/ioc_loader.py
'''

import re
from data_loader.pattern_loader import load_patterns
from nltk import sent_tokenize

from project_config import RE_PATTERNS_FILE_PATH


class iocs(object):
    def __init__(self) -> None:
        super().__init__()

    def find_them_all(self):
        lst = []
        pat = load_patterns(RE_PATTERNS_FILE_PATH)
        for key, value in pat.items():
            files = re.findall(value, self)
            if files:
                lst.append(files)
        return lst

    def list_of_iocs(self):
        ioc_list = []
        sentences = sent_tokenize(self)
        for i in sentences:
            x = iocs.find_them_all(i)
            for i in range(len(x)):
                for ioc in x[i]:
                    if len(x[i]) == 1:
                        if type(x[i][0]) == tuple:
                            ioc_list.append(x[i][0][0])
                        break
                if len(x[i]) > 1:
                    if type(x[i][0]) == tuple:
                        for k in x[i]:
                            ioc_list.append(k[0])
                    else:
                        ioc_list.append(x[i][0])
        return ioc_list
