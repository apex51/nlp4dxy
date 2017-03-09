# -*- coding: utf8 -*-

import pandas as pd
import numpy as np

import jieba

import jieba.posseg as pseg

stopwords_eng = [line.strip() for line in open('/Users/jianghao/Projects/stop words/english.txt')]
stopwords_chn = [line.strip() for line in open('/Users/jianghao/Projects/stop words/chinese.txt')]
stopwords = stopwords_eng + stopwords_chn

filter_types = ["/x","/zg","/uj","/ul","/e","/d","/uz","/y"]

index = 400

seg_list = pseg.cut(df_sql['content'][index])

print 

result = []

for word, flag in seg_list:
    word = word.encode('utf8').lower().replace(' ','')
    if word not in stopwords:
        if flag not in filter_types:
            if not word.isdigit():
                result.append(word)

print df_sql['content'][index]
print ' '.join(result)
