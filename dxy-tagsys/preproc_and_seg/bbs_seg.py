# -*- coding: utf-8 -*-

'''
- Enjoy training!
'''

import jieba
import re
import os
from datetime import datetime

jieba.load_userdict('/home/jiangh/seg_code/data/med_dxy.dic')
jieba.enable_parallel(4)

rootdir = '/home/jiangh/hive/bbs/body/'
resultdir = '/home/jiangh/result/bbs'

for subdir, dirs, files in os.walk(rootdir):
    for filename in files:
        print 'dealing with file: {}'.format(filename)
        start = datetime.now()
        with open(os.path.join(subdir, filename)) as f:
            lines = f.read()
        lines = re.sub(r'\[.+?\]', ' ', lines)
        lines = re.sub(r'(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/\.]|[~]|[%?=&_:-])+', ' ', lines)
        lines = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', lines)
        lines = re.sub(r'(。+)|(？+)', '\n', lines)
        lines = re.sub('&nbsp', ' ', lines)
        lines = ' '.join(jieba.cut(lines))
        lines = re.sub(' ', '  ', lines)
        lines = re.sub(u' [^\u03B1-\u03C9\u4E00-\u9FA5a-zA-Z0-9 \n]+ ', ' ', lines)
        lines = re.sub(u' [a-zA-Z] ', ' ', lines)
        lines = re.sub(u' \d+\.*\d* ', ' ', lines)
        lines = re.sub(u'[ ]+', ' ', lines)
        lines = re.sub(r'\n[ \n]+\n', '\n', lines)
        lines = re.sub(r' \n ', '\n', lines)
        lines = lines.lower()
        with open(os.path.join(resultdir, filename), 'wb') as f:
            f.write(lines.encode('utf8'))
        print 'time duration for file {} is: {}'.format(filename, datetime.now() - start)

# time duration is: 0:06:35.041570 on mbp
# time duration isL 0:01:30.525780 on 249