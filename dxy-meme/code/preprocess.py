# -*- coding: utf-8 -*-
# Author: Jiang Hao <jiangh@dxy.cn>

import numpy as np
import pandas as pd
import pickle
import jieba.posseg as pseg
import random

# generate positive(1), negative(0) and irrelevant(2) cases
def map_source(source):
    source = source.encode('utf8')
    if source in ['丁香园cms','医脉通', 'medsci', '环球健康', '生物360', '医学论坛网', '生物谷']:
        return 1 # positive cases
    elif source in ['网易新闻', '凤凰网', '北青网', '杭州网', '央视网', '中国政府网']:
        return 0 # negative cases
    else:
        return 2 # irrelevant cases

# mapper for inner-DataFrame use
def map_text(raw_text):
    seg_list = pseg.cut(raw_text)
    result = []
    for word, flag in seg_list:
        word = word.encode('utf8').lower().strip()
        if word not in stopwords:
            if flag not in filter_types:
                if not word.isdigit():
                    result.append(word)
    return ' '.join(result)

# preprocess and pickle dataset for later use
def data_process(FILE_PATH):
    print 'Set the FILE_PATH: {}'.format(FILE_PATH)
    print 'Reading from original SQL data ...'
    df_sql = pickle.load(open(FILE_PATH + 'pickled data/df_sql.pkl', 'rb'))
    df_month = df_sql['createDate'].apply(lambda x: x.month)
    df_day = df_sql['createDate'].apply(lambda x: x.day)

    # # of positive: 11972, # of negative: 15726 
    df_source = df_sql[(df_month==9)|(df_month==10)][['content','source']]
    df_source['flag'] = df_source['source'].apply(lambda x: map_source(x))
    df_source = df_source[df_source['flag'] != 2]

    # tune to make sample numbers even: # of positive 11972, # of negative 11972
    rows = random.sample(df_source[(df_source['source'] == '网易新闻'.decode('utf8')) | (df_source['source'] == '凤凰网'.decode('utf8'))].index, 3754)
    df_source.drop(rows, inplace=True)

    # Chinese word segmantation using jieba
    stopwords_eng = [line.strip('\n') for line in open(FILE_PATH + 'stop words/english.txt')]
    stopwords_chn = [line.strip('\n') for line in open(FILE_PATH + 'stop words/chinese.txt')]
    stopwords = stopwords_eng + stopwords_chn
    filter_types = ["/x","/zg","/uj","/ul","/e","/d","/uz","/y"]

    print 'Segmenting using jieba ...'
    segmented_content = df_source['content'].apply(lambda x: map_text(x))
    df_source['content'] = segmented_content

    print 'Pickle is dumping the dataset ...'
    with open(FILE_PATH + 'pickled data/data_set.pkl', 'wb') as f:
        pickle.dump(df_source, f)

    print 'Preprocessing done!'