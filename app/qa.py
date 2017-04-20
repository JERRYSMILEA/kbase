# -*- coding:utf-8 -*-
# @author:Eric Luo
# @file:dialog.py
# @time:2017/4/10 0010 16:04
from flask import render_template, request
from app import *
from .segment import *
from lxml import etree


def fmmcut(sentence, wordsdict1, wordsdict2, wordsdict3, FMM=True):
    result_s = []
    sentence = sentence.lower()
    s_length = len(sentence)
    if FMM:
        while s_length > 0:
            word = sentence
            w_length = len(word)
            while w_length > 0:
                if word in wordsdict1:
                    synonym = wordsdict1.get(word)
                    result_s.append("@" + synonym + "," + str(wordsdict2.get(synonym)))
                    sentence = sentence[w_length:]
                    break
                elif word in wordsdict2:
                    result_s.append("@" + word + "," + str(wordsdict2.get(word)))
                    sentence = sentence[w_length:]
                    break
                elif word in wordsdict3 or w_length == 1:
                    result_s.append(word)
                    sentence = sentence[w_length:]
                    break
                else:
                    word = word[:w_length - 1]
                w_length = w_length - 1
            s_length = len(sentence)
    else:
        while s_length > 0:
            word = sentence
            w_length = len(word)
            while w_length > 0:
                if word in wordsdict1:
                    synonym = wordsdict1.get(word)
                    result_s.insert(0, ("@" + synonym + "," + str(wordsdict2.get(synonym))))
                    sentence = sentence[:s_length - w_length]
                    break
                elif word in wordsdict2:
                    result_s.insert(0, ("@" + word + "," + str(wordsdict2.get(word))))
                    sentence = sentence[:s_length - w_length]
                    break
                elif word in wordsdict2 or w_length == 1:
                    result_s.insert(0, word)
                    sentence = sentence[:s_length - w_length]
                    break
                else:
                    word = word[1:]
                w_length = w_length - 1
            s_length = len(sentence)
    return result_s


def load_dataframe():
    dict_keyword = {}
    with open("app/dict/keyword.dict", encoding='utf8') as f:
        for line in f:
            (val, imp) = line.strip().split(',')
            dict_keyword[val] = imp
    dict_extend_item = {}
    with open("app/dict/extend_item.dict", encoding='utf8') as f:
        for line in f:
            (qa_ex_id, item) = line.strip().split(',')
            dict_extend_item[qa_ex_id] = item
    return dict_keyword, dict_extend_item


def load_qa(xml_filename):
    print("Building Question & Answer Dict...")
    # Process knowledge.xml
    tree = etree.parse(xml_filename)
    root = tree.getroot()
    dict_question, dict_answer = {}, {}
    qa_id = 0
    for knowledge in root:
        qa_id = qa_id + 1
        qa_data = []
        for field in knowledge:
            if field.text is None:
                continue
            else:
                qa_data.append(field.text.strip())
        dict_question[qa_id] = qa_data[0]
        dict_answer[qa_id] = qa_data[1]
    print("The volumn of Question & Answer Dict:", len(dict_question), len(dict_answer))
    return dict_question, dict_answer


def get_qa(dict_question, dict_answers, items):
    questions, answers = [], []
    i = 0
    print(items)
    for item in items:
        print(item)
        qa_id, ex_id = item.strip().split(':')
        print(qa_id, ex_id)
        if int(qa_id) in dict_question:
            print("Find question & answer!", i)
            i += 1
            questions.append(str(i) + ':' + dict_question.get(int(qa_id)))
            answers.append(str(i) + ':' + dict_answers.get(int(qa_id)))
    return questions, answers

dict_keyword, dict_extend_item = load_dataframe()
dict_question, dict_answer = load_qa("app/dict/knowledge.xml")


def CountPoint(dict_seg):
    with open("app/dict/extend_point.df", encoding='utf8') as f:
        best_id = ''
        best = 0
        for line in f:
            (qa_ex_id, _, _, _, _) = line.strip().split(',')
            point, max, match, unmatch = 0.0, 0.0, 0.0, 0.0
            if dict_extend_item.get(qa_ex_id) and (dict_extend_item.get(qa_ex_id) != 'Item'):
                items = dict_extend_item.get(qa_ex_id).split(';')
                items.pop(-1)
                for item in items:
                    if dict_keyword.get(item):
                        max += float(dict_keyword.get(item))
                    if dict_seg.get(item):
                        match += float(dict_keyword.get(item))
                    else:
                        unmatch += float(dict_keyword.get(item)) * 0.3
            if max != 0.0:
                point = (match - unmatch) / max
                # print(qa_ex_id, point)
                if point > best:
                    best = point
                    best_id = qa_ex_id
        print('Best ID & point:', best_id, best)
    return best_id, best


@app.route('/qa', methods=['GET', 'POST'])
@app.route('/qa/', methods=['GET', 'POST'])
def qa():
    if request.method == 'POST':
        question = request.form.get('question')
        dict_seg = {}
        best_question, best_answer = [], []
        items = []
        fmm1 = fmmcut(question, wordsdict1, wordsdict2, wordsdict3)
        print(fmm1)
        item, im = [], []
        for word in fmm1:
            if '@' in word:
                word, importance = word.strip().split(',')
                _, word = word.strip().split('@')
                dict_seg[word] = float(importance)
        print(dict_seg)
        best_id, best = CountPoint(dict_seg)
        items.append(best_id)
        best_question, best_answer = get_qa(dict_question, dict_answer, items)
        print(best_question, best_answer)
        return render_template('qa.html', qa = True, questions = best_question, answers = best_answer, )
    return render_template('qa.html',)
