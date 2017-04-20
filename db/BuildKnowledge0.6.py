# -*- coding: utf-8 -*-
from lxml import etree

xml_filename1 = 'knowledge.xml'

# Process knowledge.xml
tree = etree.parse(xml_filename1)
root = tree.getroot()

que_data = []
ans_data = []
extend_item = ['qa_ex_id,Item,canOmit,synonym']
extend_point = ['qa_ex_id,max,match,unmatch,best']
dict_extend = ['qa_ex_id,Item']
dict_extend_synonym = ['qa_ex_id,Item']
qa_id = 0
ex_no, kw_no, sy_no = 0, 0, 0

for knowledge in root:
    qa_id = qa_id + 1
    qa_data = []
    ex_id = 0
    for field in knowledge:
        if field.text is None:
            ex_id = ex_id + 1
            kw_id = 0
            extend = []
            extend_synonym = []
            qa_ex = str(qa_id) + ':' + str(ex_id)
            extend_point.append('\n' + qa_ex + ',' + '0.0' + ',' + '0.0' + ',' + '0.0' + ',' + '0.0')
            for item in field:
                row_data = []
                kw_id += 1
                for keyword in item:
                    row_data.append(keyword.text.strip())
                sy_no += len(row_data) - 2
                if len(row_data) == 2:
                    extend_item.append('\n' + qa_ex + ',' + row_data[0].lower() + ',' + row_data[1].lower())
                    extend.append(row_data[0].lower() + ';')
                    extend_synonym.append(row_data[0].lower() + ';')
                else:
                    extend_synonym.append(row_data[0].lower())
                    while len(row_data) >= 3:
                        extend_item.append('\n' + qa_ex + ',' + row_data[0].lower() + ',' + row_data[1].lower() + ',')
                        extend_item.append(row_data[-1].lower())
                        extend.append(row_data[-1].lower() + ';')
                        extend_synonym.append('|' + row_data[-1].lower())
                        row_data.pop(-1)
                    extend_synonym.append(';')
            if extend:
                dict_extend.append('\n' + qa_ex + ',')
                dict_extend.extend(extend)
                dict_extend_synonym.append('\n' + qa_ex + ',')
                dict_extend_synonym.extend(extend_synonym)
            kw_no += kw_id
        else:
            qa_data.append(field.text.strip())
    ex_no += ex_id
    que_data.append(str(qa_id) + ',' + qa_data[0] + '\n')
    ans_data.append(str(qa_id) + ',' + qa_data[1] + '\n')
print("Process QA: ", qa_id)
print("Process Extend: ", ex_no)
print("Process Keyword: ", kw_no)
print("Process Local Synonym: ", sy_no)
open('question.txt', 'w', encoding='utf8').writelines(que_data)
open('answer.txt', 'w', encoding='utf8').writelines(ans_data)
open('extend_item.df', 'w', encoding='utf8').writelines(extend_item)
open('extend_point.df', 'w', encoding='utf8').writelines(extend_point)
open('extend_item.dict', 'w', encoding='utf8').writelines(dict_extend)
open('extend_item_sy.dict', 'w', encoding='utf8').writelines(dict_extend_synonym)
print("Knowledge.xml 文件建立完成! (question.txt & answer.txt & extend_item.df & extend_point.df)")
