#!python
# -*- coding: utf-8 -*-
# @author: Kun

'''
Author: Kun
Date: 2021-09-16 11:12:03
LastEditTime: 2021-09-23 18:02:44
LastEditors: Kun
Description: 
FilePath: /ThreatReportExtractor/main.py
'''

import os
import signal
import argparse
import re
from nltk import sent_tokenize
import spacy

from nlp_extractor.tokenizer import ThreatTokenizer

from preprocessings import PreProcessor
from role_generator import RoleGenerator

from graph_generator import GraphGenerator

from data_loader.pattern_loader import load_lists
from project_config import SEC_PATTERNS_FILE_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--asterisk', type=str, default='true',
                        help='asterisk task (true, false)')
    parser.add_argument('--crf', type=str, default='true',
                        help='crf task (true, false)')
    parser.add_argument('--rmdup', type=str, default='true',
                        help='remove duplicate task (true, false)')
    parser.add_argument('--elip', type=str, default='false',
                        help='ellipsis resolution (true, false)')
    parser.add_argument('--gname', type=str,
                        default='graph', help='graph name')
    parser.add_argument('--input_file', type=str, help='input file')
    args = parser.parse_args()
    print(args)

    ########################################################################################

    nlp = spacy.load("en_core_web_lg")

    titles_list = load_lists(SEC_PATTERNS_FILE_PATH)['MS_TITLES']
    titles_list = titles_list.replace("'", "").strip('][').split(', ')

    main_verbs = load_lists(SEC_PATTERNS_FILE_PATH)['verbs']
    main_verbs = main_verbs.replace("'", "").strip('][').split(', ')

    threat_tokenizer = ThreatTokenizer(nlp, main_verbs, titles_list)

    if not args.input_file:
        raise ValueError(
            "usage: main.py [-h] [--asterisk ASTERISK] [--crf CRF] [--rmdup RMDUP] [--gname GNAME] [--input_file INPUT_FILE]")
    else:
        with open(args.input_file, encoding='iso-8859-1') as f:
            txt = f.readlines()
            txt = " ".join(txt)
            txt = txt.replace('\n', ' ')

    pre_processor = PreProcessor(nlp)

    role_gen = RoleGenerator(nlp, main_verbs)

    graph_gen = GraphGenerator()

    ########################################################################################
    # TODO moved from tokenizer
    txt = threat_tokenizer.delete_brackets(txt)
    txt = txt.strip(" ")

    all_sentences_list = threat_tokenizer.removable_token(txt)

    txt_tokenized = threat_tokenizer.sentence_tokenizer(all_sentences_list)
    print("*****sentence_tokenizer:",
          len(sent_tokenize(txt_tokenized)), threat_tokenizer.sentence_tokenizer(all_sentences_list))

    print("*****Tokenizer*****")

    for i, val in enumerate(sent_tokenize(txt_tokenized)):
        print(i, val)

    ########################################################################################
    # TODO moved from preprocessings
    def SIGSEGV_signal_arises(signalNum, stack):
        print(f"{signalNum} : SIGSEGV arises")

    signal.signal(signal.SIGSEGV, SIGSEGV_signal_arises)

    # print("[spacy] begin load en_core_web_lg")
    # nlp = spacy.load("en_core_web_lg")
    preprocessing_input = threat_tokenizer.sentence_tokenizer(
        all_sentences_list)

    print("------------communicate ---------------")

    txt = preprocessing_input
    txt = pre_processor.delete_brackets(txt)

    txt = pre_processor.pass2acti(txt)
    txt = re.sub(' +', ' ', txt)
    print("*********8", txt)

    if args.crf == 'true':
        print("args.crf is 'true'")
        print(txt)
        txt = pre_processor.coref_(txt, nlp)
        print("coref_", len(txt), txt)
    else:
        txt = pre_processor.wild_card_extansions(txt)

    txt = pre_processor.try_to(txt)
    print("try_to__", txt)
    txt = pre_processor.is_capable_of(txt)

    if args.elip == 'true':
        txt = pre_processor.replcae_surrounding_subject(txt)
    else:
        print("is capble of__", txt)
        txt = pre_processor.ellipsis_subject(txt)
        print("ellipsis_subject", len(txt), txt)

    print('------------ coref_the_following_colon ------------')
    out = pre_processor.coref_the_following_colon(txt)

    for i, val in enumerate(sent_tokenize(out)):
        print(i, val)

    print('------------ coref_the_following_middle ------------')

    midle = pre_processor.coref_the_following_middle(out)

    for i, val in enumerate(sent_tokenize(midle)):
        print(i, val)

    out_translate = pre_processor.translate_obscure_words(out)
    print("*****homogenization:", pre_processor.homogenization(out_translate))
    homo = pre_processor.homogenization(out_translate)
    comm = pre_processor.communicate_to_sr(homo)
    print(comm)
    cc = pre_processor.CـC(comm)

    print("------------ modification ---------------")

    print('----Preprocessed:----')
    for i, val in enumerate(sent_tokenize(pre_processor.modification_(cc))):
        print(i, val)

    ########################################################################################
    # TODO removed from role_generator
    # main_verbs = load_lists(SEC_PATTERNS_FILE_PATH)['verbs']
    # main_verbs = main_verbs.replace("'", "").strip('][').split(', ')

    ########################################################################################

    txt = pre_processor.modification_(cc)
    txt = txt.strip()
    txt = role_gen.colon_seprator_multiplication(txt)

    txt = re.sub(' +', ' ', txt)
    sentences_ = sent_tokenize(txt)

    # TODO Role Generator
    lst = role_gen.roles(sentences_)
    lst = role_gen.fix_srl_spacing(lst)
    all_nodes = role_gen.negation_clauses(lst)
    if args.asterisk == 'true':
        all_nodes = role_gen.astriks(all_nodes)
        all_nodes = role_gen.triplet_builder(all_nodes)
    else:
        all_nodes = role_gen.triplet_builder(all_nodes)

    ########################################################################################

    all_nodes = graph_gen.remove_no_sub(all_nodes)
    lst = graph_gen.remove_c_colon_toprevent_graphvizbug(all_nodes)
    for i in lst:
        if "\\'" in i:
            i.replace("\\'", "'")

    if args.rmdup == "true":
        lst = graph_gen.rm_duplictes(lst)
        graph_gen.graph_builder(lst, args.gname)
    else:
        graph_gen.graph_builder(lst, args.gname)
