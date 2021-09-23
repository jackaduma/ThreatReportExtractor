#!python
# -*- coding: utf-8 -*-
# @author: Kun

'''
Author: Kun
Date: 2021-09-16 11:21:53
LastEditTime: 2021-09-23 18:01:15
LastEditors: Kun
Description: 
FilePath: /ThreatReportExtractor/graph_generator.py
'''


import re

from graphviz import Digraph
from data_loader.pattern_loader import load_patterns
from data_loader.ioc_loader import iocs
# import main
# import argparse

from project_config import RE_PATTERNS_FILE_PATH


################################################################################################

class edge(object):
    def __init__(self, s, d, t):
        self.src = s
        self.dst = d
        self.tag = t


class node(object):

    def __init__(self, i, n, t):
        self.id = i
        self.name = n
        self.type = t
        self.search = []

        self.reachToIDs = set()
        self.reachFromIDs = set()


class graph(object):
    def __init__(self):
        self.nodes = {}
        self.edges = []

################################################################################################


class GraphGenerator(object):
    def __init__(self) -> None:
        super(GraphGenerator, self).__init__()

    def remove_no_sub(self, lis):
        all_with_subs = []
        for i in range(len(lis)):
            if lis[i][0].split(": ", 1)[0].lower() != "v":
                all_with_subs.append(lis[i])
        return all_with_subs

    def remove_c_colon_toprevent_graphvizbug(self, lis):
        # : causes error in graphviz
        for i in lis:
            for ind, j in enumerate(i):
                if "C:\\" in j:
                    i[ind] = j.replace("C:\\", "")
                elif "D:\\" in j:
                    i[ind] = j.replace("D:\\", "")
                elif "E:\\" in j:
                    i[ind] = j.replace("E:\\", "")
                elif "F:\\" in j:
                    i[ind] = j.replace("F:\\", "")
                elif "G:\\" in j:
                    i[ind] = j.replace("G:\\", "")
                elif "H:\\" in j:
                    i[ind] = j.replace("H:\\", "")
                elif "I:\\" in j:
                    i[ind] = j.replace("I:\\", "")
                else:
                    continue
        return lis

    def rm_duplictes(self, lst):
        no_dup = []
        for x in lst:
            if x not in no_dup:
                no_dup.append(x)
            elif iocs.list_of_iocs(str(x)):
                no_dup.append(x)
        return no_dup

    ################################################################################################

    def harsh_rm_duplictes(self, lst):
        no_dup = []
        for x in lst:
            if x not in no_dup:
                no_dup.append(x)
            elif iocs.list_of_iocs(str(x)):
                no_dup.append(x)
        return no_dup

    def is_house(self, stri):
        if re.findall(load_patterns(RE_PATTERNS_FILE_PATH)['Registry'], stri):
            return True
        else:
            return False

    ################################################################################################

    def graph_builder(self, lst, gname):
        # malware_name_dot = main.args.gname + ".dot"
        malware_name_dot = gname + ".dot"
        g = Digraph(malware_name_dot, filename=malware_name_dot)
        g.body.extend(
            ['rankdir="LR"', 'size="9"', 'fixedsize="false"', 'splines="true"', 'nodesep=0.3', 'ranksep=0', 'fontsize=10', 'overlap="scalexy"',
             'engine= "neato"'])

        for index, item in enumerate(lst):
            if len(item) < 3:
                lst.pop(index)
        for index, item in enumerate(lst):
            if len(item) < 3:
                lst.pop(index)
        edge_counter = 1
        for i in range(len(lst)):
            sub = repr(lst[i][0].split(": ", 1)[1])
            vrb = repr(lst[i][1].split(": ", 1)[1])
            obj = repr(lst[i][2].split(": ", 1)[1])
            if len(lst[i]) == 3:
                xx = lst[i]
                if lst[i][1].split(": ", 1)[0].lower() == "v":
                    if vrb == '\'exec\'':
                        copy_2 = ".*\\" + lst[i][2].split(": ", 1)[1]
                        g.node(sub, shape='box', node_type="Process")
                        g.node(obj, shape='box', node_type="Process")
                        g.edge(sub, obj, label=str(
                            edge_counter) + ': ' + "fork")

                        g.node(sub, shape='box', node_type="Process")
                        g.node(copy_2, shape='ellipse', node_type="File")
                        g.edge(sub, copy_2, label=str(
                            edge_counter) + ': ' + 'exec')

                    elif vrb == '\'fork\'':
                        g.node(sub, shape='box', node_type="Process")
                        g.node(obj, shape='box', node_type="Process")
                        g.edge(sub, obj, label=str(
                            edge_counter) + ': ' + 'fork')

                    elif vrb == '\'read\'' or vrb == '\'load\'':
                        if self.is_house(obj):
                            g.node(obj, shape='house', node_type="registry")
                            g.node(sub, shape='box', node_type="Process")
                            g.edge(obj, sub, label=str(
                                edge_counter) + ': ' + vrb)
                        else:
                            g.node(obj, shape='ellipse', node_type="file")
                            g.node(sub, shape='box', node_type="Process")
                            g.edge(obj, sub, label=str(
                                edge_counter) + ': ' + vrb)

                    elif vrb == '\'receive\'':
                        if sub == obj:
                            y = " IP " + obj
                            g.node(y, shape='diamond', node_type="file")
                            g.node(sub, shape='box', node_type="Process")
                            g.edge(y, sub, label=str(
                                edge_counter) + ': ' + vrb[1:-1])
                        else:
                            g.node(obj, shape='diamond', node_type="file")
                            g.node(sub, shape='box', node_type="Process")
                            g.edge(obj, sub,
                                   label=str(edge_counter) + ': ' + vrb[1:-1])

                    elif vrb.strip() == '\'write\'' or vrb.strip() == '\'unlink\'':
                        if self.is_house(obj):
                            g.node(obj, shape='house', node_type="registry")
                            g.node(sub, shape='box', node_type="Process")
                            g.edge(sub, obj, label=str(
                                edge_counter) + ': ' + vrb[1:-1])
                        else:
                            g.node(obj, shape='ellipse', node_type="file")
                            g.node(sub, shape='box', node_type="Process")
                            g.edge(sub, obj, label=str(
                                edge_counter) + ': ' + vrb[1:-1])

                    elif vrb.strip() == '\'send\'':
                        if sub == obj:
                            x = " IP " + obj
                            g.node(x, shape='diamond')
                            g.node(sub, shape='box')
                            g.edge(sub, x,
                                   label=str(edge_counter) + ': ' + vrb[1:-1])
                        else:
                            g.node(obj, shape='diamond')
                            g.node(sub, shape='box')
                            g.edge(sub, obj,
                                   label=str(edge_counter) + ': ' + vrb[1:-1])

                    elif vrb != '\'fork\'' or vrb != '\'exec\'' or vrb != '\'read\'' or vrb != '\'load\'' or vrb != '\'write\'' or vrb != '\'send\'' or vrb != '\'unlink\'':
                        if lst[i][1].split(": ", 1)[0].lower() == "v":

                            if self.is_house(obj):
                                g.node(obj, shape='house',
                                       node_type="registry")
                                g.node(sub, shape='box', node_type="Process")
                                g.edge(sub, obj, label=str(
                                    edge_counter) + ': ' + vrb[1:-1])
                            else:
                                g.node(obj, shape='ellipse', node_type="file")
                                g.node(sub, shape='ellipse', node_type="file")
                                # g.edge(sub, obj, label=str(edge_counter) + ': ' + vrb)
                                g.edge(sub.__str__().replace("'", ""), obj.__str__().replace(
                                    "'", ""), label=str(edge_counter) + ': ' + vrb[1:-1])

                    else:
                        print("*********EXCEPTION : ", lst[i])

                else:
                    print('**************** EXCEPTION ****************')
                    print('******', lst[i], '******')
                    print('**************** EXCEPTION ****************')

                edge_counter += 1

        g.view()
