# -*- coding: utf-8 -*-

import jieba
import re
import os
from datetime import datetime

jieba.load_userdict('/home/jiangh/seg_code/data/med_dxy.dic')
jieba.enable_parallel(4)

rootdir = '/home/jiangh/hive/weixin/000000_0'
resultdir = '/home/jiangh/result/weixin/000000_0'

character_map_path = '/home/jiangh/seg_code/data/character_map'
cjk_map_path = '/home/jiangh/seg_code/data/cjk_map'

start = datetime.now()

with open(rootdir) as f:
    lines = f.read()
# cleasing &x; html code
# first iterate &abc; to character
with open(character_map_path) as f:
    character_map = f.readlines()
for character_item in character_map:
    character_item = re.split('[ ]+', character_item)
    character, code = character_item[0], character_item[2]
    lines = re.sub(code, character, lines)
# then iterate $#123; to character
with open(character_map_path) as f:
    character_map = f.readlines()
for character_item in character_map:
    character_item = re.split('[ ]+', character_item)
    character, code = character_item[0], character_item[1]
    lines = re.sub(code, character, lines)
# cleasing CJK Compatibility Ideograph html code to simplified chinese
with open(cjk_map_path) as f:
    cjk_map = f.readlines()
for cjk_item in cjk_map:
    cjk_item = re.split('[ ]+', cjk_item)
    character, code = cjk_item[0], cjk_item[2]
    lines = re.sub('&#'+code+';', character, lines)
# &nbsp; is white space, which should do seperately
lines = re.sub(r'&nbsp;', ' ', lines) 
lines = re.sub(r'<.+?>', ' ', lines)
lines = re.sub(r'(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/\.]|[~]|[%?=&_;:-])+', ' ', lines)
lines = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', lines) 
lines = re.sub(r'\x01', '\n', lines) # sub ^A
lines = re.sub(r'(。+)|(？+)', '\n', lines)
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