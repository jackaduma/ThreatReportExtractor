#!python
# -*- coding: utf-8 -*-
# @author: Kun

'''
Author: Kun
Date: 2021-09-16 14:08:49
LastEditTime: 2021-09-23 17:05:56
LastEditors: Kun
Description: 
FilePath: /ThreatReportExtractor/nlp_extractor/tokenizer.py
'''

import spacy
from nltk import sent_tokenize

from data_loader.pattern_loader import load_lists
from project_config import SEC_PATTERNS_FILE_PATH

# import main


# nlp = spacy.load("en_core_web_lg")
# if not main.args.input_file:
#     raise ValueError(
#         "usage: main.py [-h] [--asterisk ASTERISK] [--crf CRF] [--rmdup RMDUP] [--gname GNAME] [--input_file INPUT_FILE]")
# else:
#     with open(main.args.input_file, encoding='iso-8859-1') as f:
#         txt = f.readlines()
#         txt = " ".join(txt)
#         txt = txt.replace('\n', ' ')

# titles_list = load_lists(SEC_PATTERNS_FILE_PATH)['MS_TITLES']
# titles_list = titles_list.replace("'", "").strip('][').split(', ')
# main_verbs = load_lists(SEC_PATTERNS_FILE_PATH)['verbs']
# main_verbs = main_verbs.replace("'", "").strip('][').split(', ')

class ThreatTokenizer(object):
    def __init__(self, nlp, main_verbs, titles_list) -> None:
        super(ThreatTokenizer, self).__init__()

        self.nlp = nlp

        self.main_verbs = main_verbs

        self.titles_list = titles_list

    ########################################################################################

    def delete_brackets(self, stri):
        stri = stri.replace("[", "")
        stri = stri.replace("]", "")
        stri = stri.replace("<", "")
        stri = stri.replace(">", "")
        return stri

    # txt = delete_brackets(txt)
    # txt = txt.strip(" ")

    ########################################################################################

    def all_sentences(self, string):
        nltk_sentences = sent_tokenize(string)

        all_sentences_list = []
        for i in nltk_sentences:
            i.rstrip()
            if i.endswith(".") and "\n" not in i:
                all_sentences_list.append(i)
            elif "\n" in i:
                i.split("\n")
                for j in i.split("\n"):
                    all_sentences_list.append(j)
        return all_sentences_list

    def remove_analysis_by(self, txt):
        var = "Analysis by"
        lst = self.all_sentences(txt)
        for i in lst:
            if i.startswith(var):
                lst.remove(i)
        return lst

    def perform_following_action(self, txt):
        # When Virus:Win32/Funlove.4099 runs, it performs the following actions:
        perform_following_action_list = load_lists(
            SEC_PATTERNS_FILE_PATH)['MS_PFA']
        perform_following_action_list = perform_following_action_list.replace(
            "'", "").strip('][').split(', ')
        lst = self.remove_analysis_by(txt)
        for i in lst:
            for j in perform_following_action_list:
                if j in i:
                    lst.remove(i)
                    break
        return lst

    def on_the_windows_x_only(self, txt):
        # on_the_windows_x_list = load_lists_microsoft.on_the_windows_x_lst()
        on_the_windows_x_list = load_lists(SEC_PATTERNS_FILE_PATH)['MS_OTW']
        on_the_windows_x_list = on_the_windows_x_list.replace(
            "'", "").strip('][').split(', ')
        lst = self.perform_following_action(txt)
        for i in lst:
            for j in on_the_windows_x_list:
                if j == i:
                    lst.remove(i)
                    # break
        return lst

    def removable_token(self, txt):
        # When Virus:Win32/Funlove.4099 runs, it performs the following actions:
        removable_token_list = load_lists(SEC_PATTERNS_FILE_PATH)['RTL']
        removable_token_list = removable_token_list.replace(
            "'", "").strip('][').split(', ')
        lst = self.on_the_windows_x_only(txt)
        for id, value in enumerate(lst):
            for j in removable_token_list:
                if value.strip().startswith(j):  # definetly remember we should use only startswith()for proper matching
                    # lst.remove(value)
                    lst[id] = value.replace(j, " ")
                    # break
        return lst

    # all_sentences_list = removable_token()
    ########################################################################################

    # handles titles and "." of the previous sentence
    def handle_title(self, mylist_):
        lst_handled_titles = []
        lst = list(filter(lambda a: a != "", mylist_))[::-1]
        lst = list(filter(lambda a: a != " ", lst))
        lst = list(filter(lambda a: a != "", lst))
        for indx, val in enumerate(lst):
            lst[indx] = val.strip()
            if val == '':
                del lst[indx]
        l = len(lst)
        for index, item in enumerate(lst):
            if index < l - 1:
                if item in self.titles_list:
                    x = lst[index + 1]
                    if lst[index + 1] not in self.titles_list:
                        if len(lst[index + 1].rstrip()) >= 1:  # inja
                            if lst[index + 1].rstrip()[-1] != ".":
                                if lst_handled_titles:
                                    if lst[index + 1] + "." != lst_handled_titles[-1]:
                                        lst_handled_titles.append(
                                            lst[index + 1] + ".")
                                else:
                                    lst_handled_titles.append(
                                        lst[index + 1] + ".")
                            else:
                                if lst_handled_titles:
                                    if lst[index + 1] != lst_handled_titles[-1]:  # mahshid added n
                                        lst_handled_titles.append(
                                            lst[index + 1])
                                else:
                                    lst_handled_titles.append(lst[index + 1])
                    else:
                        pass
                else:
                    if lst_handled_titles:
                        if item + "." not in lst_handled_titles and item != lst_handled_titles[-1]:
                            lst_handled_titles.append(item)
                    else:

                        lst_handled_titles.append(item)
            else:
                if item not in self.titles_list:
                    if item != lst_handled_titles[-1]:
                        lst_handled_titles.append(item)
        lst = lst_handled_titles[::-1]
        lst = list(filter(lambda a: a != " ", lst))
        return list(filter(lambda a: a != "", lst))

    def zero_word_verb(self, string):
        doc = self.nlp(string.strip())
        if not (doc[0].tag_ == "MD") and\
                not (doc[0].tag_ == "VB" and
                     str(doc[0]).lower() in self.main_verbs) and\
                not (doc[0].tag_ == "VB" and
                     str(doc[0]).lower() not in self.main_verbs) and\
                not(str(doc[0]).lower() in self.main_verbs):
            return False
        else:
            return True

    def true_sentence(self, sentence):
        if len(sent_tokenize(sentence)) > 0:
            return True
        return False

    def iscaptalized(self, sentence):
        if sentence.strip()[0].isupper() == True:
            return True
        else:
            return False

    def sentence_characteristic(self, sentence):
        doc = self.nlp(sentence)
        if len(sentence.split(" ")) > 3:
            count_verb, count_noun = 0, 0
            for token in doc:
                if token.pos_ == "VERB":
                    count_verb += 1
                if token.pos_ == "NOUN":
                    count_noun += 1
            if count_verb >= 1 and count_noun >= 2:
                return True
        else:
            return False

    def likely_sentence_characteristic(self, sentence):
        doc = self.nlp(sentence)
        if self.zero_word_verb(sentence) == True:
            if len(sentence.split(" ")) > 3:
                return True

            return "UNKNOWN"

        if self.iscaptalized(sentence) == True:
            if len(sentence.split(" ")) > 3:
                count_verb, count_noun = 0, 0
                for token in doc:
                    if token.pos_ == "VERB":
                        count_verb += 1
                    if token.pos_ == "NOUN":
                        count_noun += 1
                if count_verb >= 1 and count_noun >= 2:
                    return True
        else:
            return False

    def sentence_tokenizer(self, all_sentences_list):
        num = 0
        possible_sentence = ""
        sentnce_buffer = ""
        if len(all_sentences_list) > 1:
            handele_titles = self.handle_title(all_sentences_list)
        else:
            handele_titles = all_sentences_list
        sentences_list = []
        for sec in handele_titles:
            # sentences_list.append(sec.encode('ascii', errors='ignore').decode('utf8'))
            sentences_list.append(sec.replace(u'\xa0', u' '))
        # remvoe ' '  from handle list
        sentences_list = list(filter(lambda a: a != " ", sentences_list))
        sentences_list = list(filter(lambda a: a != "  ", sentences_list))
        sentences_list = list(filter(lambda a: a != "   ", sentences_list))
        l = len(sentences_list)

        for i in range(len(sentences_list)):
            other_sentences = []
            if num == l:
                break
            if num < l:
                xyz = sentences_list[i]
                if sentences_list[i].rstrip()[-1] == ".":
                    if self.sentence_characteristic(sentences_list[i]) == True:
                        possible_sentence += sentences_list[i] + " "
                        num += 1
                    elif len(sentences_list[i].split(" ")) > 3 and sentences_list[i].split(" ")[0].lower() in self.main_verbs:
                        possible_sentence += sentences_list[i] + " "
                        num += 1
                    else:
                        print("ELSE-1:", sentences_list[i])
                        possible_sentence += sentences_list[i] + " "
                        num += 1
                elif self.zero_word_verb(sentences_list[i]) and ":" not in sentences_list[i].strip():
                    if num != l - 1:
                        if self.sentence_characteristic(sentences_list[i + 1]) == True or self.zero_word_verb(sentences_list[i + 1]):
                            possible_sentence += sentences_list[i].strip() + \
                                " . "
                            num += 1
                        elif self.sentence_characteristic(sentences_list[i + 1]) == False or not self.zero_word_verb(sentences_list[i + 1]):
                            sentnce_buffer += sentences_list[i].strip()
                            num += 1
                            sentnce_buffer += sentences_list[i + 1]
                            num += 1
                    else:
                        possible_sentence += sentences_list[i].strip() + " . "
                        num += 1

                elif self.zero_word_verb(sentences_list[i]) and ":" in sentences_list[i]:
                    # or [i+1] is likely_sentence_ ...
                    if not self.zero_word_verb(sentences_list[i + 1]):
                        sentnce_buffer += sentences_list[i] + " "
                        num += 1
                        # if zero_word_verb(sentences_list[i+1]):
                        if num < l:
                            # whattttt? #######!!!!!!!!######## or sentences_list[i+1].rstrip()[-1]!="." BELOWWW
                            while not self.likely_sentence_characteristic(sentences_list[i + 1]):
                                # or sentence_characteristic(sentences_list[i+1]) ==True and sentences_list[i+1].rstrip()[-1]!="."
                                sentnce_buffer += sentences_list[i + 1] + " "
                                num += 1
                                sentences_list[i + 1]
                                del sentences_list[i + 1]
                                if num == l:
                                    break
                            sentnce_buffer += " . "
                            possible_sentence += " "
                            possible_sentence += sentnce_buffer
                            sentnce_buffer = ""

                        elif sentences_list[i].strip()[-1] == ":":
                            possible_sentence += sentences_list[i].replace(
                                ":", " . ") + " "
                            num += 1
                        else:  # Creates registry value: gigabit.exe
                            possible_sentence += sentences_list[i] + " . "
                            num += 1
                        # if num < l:
                        #     sentnce_buffer += sentences_list[i+1] + " "
                        #     num += 1
                        #     del sentences_list[i+1]
                        #     while not zero_word_verb(sentences_list[i+1]):
                        #         sentnce_buffer += sentences_list[i + 1]  + " "
                        #         num += 1
                        #         del sentences_list[i + 1]
                        #     sentnce_buffer += " . "
                        #     possible_sentence += sentnce_buffer
                        # else:
                        #     break
                    elif self.zero_word_verb(sentences_list[i + 1]):
                        if sentences_list[i].rstrip()[-1] == ":":
                            possible_sentence += sentences_list[i].replace(
                                ":", " . ") + " "
                            num += 1
                        else:
                            possible_sentence += sentences_list[i] + " . "
                            num += 1

                elif self.iscaptalized(sentences_list[i]) == True and sentences_list[i].rstrip()[-1] == ":":
                    if sentences_list[i] == sentences_list[-1]:
                        possible_sentence += sentences_list[i].replace(
                            ":", " . ") + " "
                        num += 1

                    elif self.zero_word_verb(sentences_list[i + 1]):
                        possible_sentence += sentences_list[i].replace(
                            ":", " . ") + " "
                        num += 1
                    else:
                        sentnce_buffer += sentences_list[i] + " "
                        num += 1
                        while not(self.sentence_characteristic(sentences_list[i + 1])):
                            xxx = sentences_list[i + 1]
                            if self.zero_word_verb(sentences_list[i + 1]):
                                break

                            elif not self.zero_word_verb(sentences_list[i + 1]):
                                sentnce_buffer += sentences_list[i + 1] + " "
                                num += 1
                                del sentences_list[i + 1]
                                if num == l or num > l:
                                    if sentnce_buffer.rstrip()[-1] != ".":
                                        sentnce_buffer += " . "
                                    possible_sentence += sentnce_buffer
                                    sentnce_buffer = ""
                                    break
                        # if not sentence_characteristic(sentences_list[i + 1]):
                        #     sentnce_buffer += sentences_list[i + 1]
                        #     num += 1
                        #     del sentences_list[i + 1]
                        if sentnce_buffer:
                            if sentnce_buffer.rstrip()[-1] != ".":
                                sentnce_buffer += " . "
                        possible_sentence += sentnce_buffer
                        sentnce_buffer = ""
                        # else:
                        #     sentnce_buffer.rstrip().replace(":",".")
                        #     possible_sentence += sentnce_buffer
                        #     sentnce_buffer = " "
                elif self.sentence_characteristic(sentences_list[i]) == True:
                    possible_sentence += sentences_list[i].strip() + " . "
                    num += 1
                else:
                    other_sentences.append(sentences_list[i])
                    num += 1
            else:
                break
        posslist = sent_tokenize(possible_sentence)
        for indx, val in enumerate(posslist):
            if len(val.split()) < 2:
                del posslist[indx]
        possible_sentence = " ".join(posslist)
        return possible_sentence

    # txt_tokenized = sentence_tokenizer()
    # print("*****sentence_tokenizer:",
    #       len(sent_tokenize(txt_tokenized)), sentence_tokenizer())

    # print("*****Tokenizer*****")

    # for i, val in enumerate(sent_tokenize(txt_tokenized)):
    #     print(i, val)
