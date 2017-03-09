# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import random
import pickle
import json
import MySQLdb
import jieba.posseg as pseg
from pandas.tslib import Timestamp
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics.pairwise import pairwise_distances
import time
import schedule
from datetime import datetime


# filter news from these sources
SOURCES_FILTER = [u'丁香园bbs', u'丁香园cms', u'报纸']
SOURCES_RENAME = {'medsci': 'MedSci'}
# map source names according to the dict
def map_source(raw_source):
    if raw_source in SOURCES_RENAME.keys():
        return SOURCES_RENAME[raw_source]
    else:
        return raw_source

# mapper for inner-DataFrame use，cut, filter and join
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

###########################################################
# do the training for filtering
###########################################################
# load training data used for filtering
with open('../data/dataset_train.pkl', 'rb') as f:
    df_source = pickle.load(f)
# sample 20000 news for training, these were already cut, filtered and joint before hand.
negative_rows = random.sample(df_source[df_source['flag'] == 0].index, 10000)
positive_rows = random.sample(df_source[df_source['flag'] == 1].index, 10000)
rows = negative_rows + positive_rows
df_train = df_source.ix[rows]
# feature transformation
vectorizer = TfidfVectorizer(encoding='utf8')
x_train = vectorizer.fit_transform(df_train['content'])
y_train = df_train['flag']
# train logistic regression using SGD
clf = SGDClassifier(loss='log', penalty='l2', n_iter=50, alpha=0.00001, fit_intercept=True)
clf.fit(x_train, y_train)


###########################################################
# read remote news, filter
###########################################################
remote_con = MySQLdb.connect(host='192.168.200.208', port=3306, user='ruby_daily', passwd='dLhQjH2tyhGZLHxCRMq3', db='infocrawl', charset='utf8')
# df_sql = pd.read_sql("select id, title, summary, content, createDate, publishDate, source, sourceUrl from info_push_source where date(createDate) = '{}'".format(date.today()), con=remote_con)
df_sql = pd.read_sql("select id, title, summary, content, createDate, publishDate, source, sourceUrl from info_push_source where createDate >= '2015-11-20 00:00:00' and createDate <= '2015-11-09 23:59:59'", con=remote_con)
# with open('../data/df_sql_1109.pkl') as f:
#     df_sql = pickle.load(f)
print 'original df_sql len is {}'.format(len(df_sql))
# Chinese word segmantation using jieba
stopwords_eng = [line.strip('\n') for line in open('stopwords/english.txt')]
stopwords_chn = [line.strip('\n') for line in open('stopwords/chinese.txt')]
stopwords = stopwords_eng + stopwords_chn
filter_types = ["/x","/zg","/uj","/ul","/e","/d","/uz","/y"]
print 'Segmenting using jieba ...'
segmented_content = df_sql['content'].apply(lambda x: map_text(x))
df_sql['content'] = segmented_content
# transfer test data and filter
x_test = vectorizer.transform(df_sql['content'])
y_test = clf.predict(x_test)
df_sql = pd.DataFrame(df_sql[(y_test == 1) & (df_sql['source'].apply(lambda x: True if x not in SOURCES_FILTER else False))])
df_sql['source'] = df_sql['source'].apply(lambda x: map_source(x))

###########################################################
# dump and load for test purpose, in formal program, delete
###########################################################

# # dump data for test purpose
# with open('data/df_sql.pkl', 'wb') as f:
#     pickle.dump(df_sql, f)

# # load data for test purpose
# with open('data/df_sql.pkl', 'rb') as f:
#     df_sql = pickle.load(f)

###########################################################
# read specific tags from txt
###########################################################
doc_tags = ' '.join([' '.join(line.strip().split()[1:]) for line in open('tags/心血管科疾病词汇.txt')])

###########################################################
# find similar news, cluster
###########################################################
# fit a new vectorizer (in case that words are more updated and local in the specific day)
vectorizer_new = TfidfVectorizer(encoding='utf8')
vectorizer_new.fit(df_sql['content'].append(pd.Series(doc_tags)))
m_tfidf = vectorizer_new.transform(df_sql['content'])
m_tags = vectorizer_new.transform([doc_tags])
# calc a distance list, filter, and keep related docs
tag_distance = pairwise_distances(m_tfidf, m_tags, metric='cosine')
related_index, _ = np.where(tag_distance < 0.99)

columns = ['source_id', 'title', 'summary', 'fetch_at', 'publish_at', 'source', 'source_url', 'info_sources', 'created_at']
df_newslist = pd.DataFrame(columns=columns)
for list_news in related_index:
    dict_onepiece = {}
    dict_onepiece['source_id'] = df_sql.iloc[list_news]['id']
    dict_onepiece['title'] = df_sql.iloc[list_news]['title']
    dict_onepiece['summary'] = df_sql.iloc[list_news]['summary']
    dict_onepiece['fetch_at'] = pd.to_datetime(df_sql.iloc[list_news]['createDate'], 'coerce')
    dict_onepiece['publish_at'] = pd.to_datetime(df_sql.iloc[list_news]['publishDate'], 'coerce')
    dict_onepiece['source'] = df_sql.iloc[list_news]['source']
    list_sources = [dict_onepiece['source']] # filter multiple docs from same source
    dict_onepiece['source_url'] = df_sql.iloc[list_news]['sourceUrl']
    dict_onepiece['created_at'] = Timestamp('now')
    dict_onepiece['info_sources'] = None
    df_newslist = df_newslist.append(dict_onepiece, ignore_index=True)

# delete today's all the old news list
local_con = MySQLdb.connect(host='192.168.200.100', port=3306, user='root', passwd='', db='dxydaily', charset='utf8')
# write in the latest news list
df_newslist.to_sql(name='articles', con=local_con, flavor='mysql', if_exists='append', index=False)
print 'Job done at {}'.format(datetime.now())





