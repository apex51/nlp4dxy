# -*- coding: utf-8 -*-

'''
Disease text has no html code &#123, no email address
'''

import jieba
import re
import os
from datetime import datetime

jieba.load_userdict('/home/jiangh/seg_code/data/med_dxy.dic')
jieba.enable_parallel(4)

rootdir = '/home/jiangh/hive/disease/000000_0'
resultdir = '/home/jiangh/result/disease/000000_0_paragraph'

start = datetime.now()

with open(rootdir) as f:
    lines = f.read()
lines = re.sub(r'&nbsp;', ' ', lines) 
lines = re.sub(r'<sub>(.+?)</sub>', r'\1', lines)
lines = re.sub(r'<SUB>(.+?)</SUB>', r'\1', lines)
lines = re.sub(r'<sup>(.+?)</sup>', r'\1', lines)
lines = re.sub(r'<SUP>(.+?)</SUP>', r'\1', lines)
lines = re.sub(r'\x01', '\n', lines) # sub ^A
lines = re.sub(r'(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/\.]|[~]|[%?=&_;:-])+', ' ', lines)
lines = re.sub(r'<.+?>', ' ', lines)
# lines = re.sub(r'(。+)|(？+)|(；+)', '\n', lines)
lines = ' '.join(jieba.cut(lines))
lines = re.sub(' ', '  ', lines)
lines = re.sub(u' [^\u03B1-\u03C9\u4E00-\u9FA5a-zA-Z0-9 \n]+ ', ' ', lines)
lines = re.sub(u' [a-zA-Z] ', ' ', lines)
lines = re.sub(u' \d+\.*\d* ', ' ', lines)
lines = re.sub(u'[ ]+', ' ', lines)
lines = re.sub(r'\n[ \n]+\n', '\n', lines)
lines = re.sub(r' \n ', '\n', lines)
lines = lines.lower()
with open(resultdir, 'wb') as f:
    f.write(lines.encode('utf8'))

print 'time duration is {}'.format(datetime.now() - start)