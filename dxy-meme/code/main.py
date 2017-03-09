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

import gc

import csv

# source list to keep
SOURCES_FILTER = []
with open('sources/seed_list.csv') as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        SOURCES_FILTER.append(int(row[0]))

def filter_source(site_id):
    if site_id in SOURCES_FILTER:
        return True
    return False

# mapper for inner-DataFrame use，pseg, filter (stopwords/types)  and join
stopwords_eng = [line.strip('\n') for line in open('stopwords/english.txt')]
stopwords_chn = [line.strip('\n') for line in open('stopwords/chinese.txt')]
stopwords = stopwords_eng + stopwords_chn
filter_types = ["/x","/zg","/uj","/ul","/e","/d","/uz","/y"]

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

# training SGD classifier from training data
with open('../data/dataset_train.pkl') as f:
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


def job():

    ###########################################################
    # read remote news, filter
    ###########################################################
    while(True):
        try:
            remote_con = MySQLdb.connect(host='192.168.200.208', port=3306, user='ruby_daily', passwd='dLhQjH2tyhGZLHxCRMq3', db='infocrawl', charset='utf8')
        except MySQLdb.OperationalError, e:
            print 'MySQL Exception! Waiting for MySQL return to normal after 5 seconds ~'
            time.sleep(5)
            continue
        break
    
    # Note: the order is crescent by time, so the head is always 00:00 and followed by later news.
    df_sql = pd.read_sql("select id, title, summary, content, createDate, publishDate, source, sourceUrl, siteId from info_push_source where date(createDate) = '{}'".format(date.today()), con=remote_con)
    
    print 'original df_sql len is {}'.format(len(df_sql))
    # filter source not in source list
    df_sql = df_sql[df_sql['siteId'].apply(filter_source)]
    print 'filtered df_sql len is {}'.format(len(df_sql))
    # check, if the list is empty, return for Mama!
    if not len(df_sql):
        return

    # Chinese word segmantation using jieba
    print 'Segmenting using jieba ...'
    df_sql['content'] = df_sql['content'].apply(lambda x: map_text(x))
    # transfer test data and filter
    x_test = vectorizer.transform(df_sql['content'])
    y_test = clf.predict(x_test)
    df_sql = pd.DataFrame(df_sql[y_test == 1])
    print 'predicted df_sql len is {}'.format(len(df_sql))

    # make sure df_sql is longer than 4, or else return
    if len(df_sql) < 5:
        print 'life is too short, so use python :)'
        return

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
    # find similar news, cluster
    ###########################################################
    # fit a new vectorizer (in case that words are more updated and local in the specific day)
    vectorizer_new = TfidfVectorizer(encoding='utf8', max_df=0.5, min_df=2)
    m_tfidf = vectorizer_new.fit_transform(df_sql['content'])
    # pairwise distance
    m_distance = pairwise_distances(m_tfidf, metric='cosine')
    # m_distance[np.diag_indices_from(m_distance)] = 1.0
    # a true or false mask
    m_check = m_distance < 0.4
    # only consider the upper right triangle, include the diagonal
    for i in range(m_check.shape[0]):
        for j in range(m_check.shape[1]):
            if i >= j:
                m_check[i, j] = False
    indices_row, indices_col = np.where(m_check)
    # clustering 
    dict_cluster = {}
    i_dict = 0
    for row, col in zip(indices_row, indices_col):
        # check if dict already has index: if yes, put the other index in
        has_row = False
        for key in dict_cluster:
            if row in dict_cluster[key]:
                has_row = True
                if col not in dict_cluster[key]:
                    dict_cluster[key].append(col)
                break
        if has_row is False:
            if row == col:
                dict_cluster[i_dict] = [row]
            else:
                dict_cluster[i_dict] = [row, col]
            i_dict += 1
    # # map from index to source_id
    # for key in dict_cluster:
    #     dict_cluster[key] = map(lambda x: df_sql.iloc[x]['id'], dict_cluster[key])

    # order by pure create time (ie. fetch_at)
    # please note that the order is crescent
    list_cluster = sorted(dict_cluster.items(), key=lambda x: df_sql.iloc[x[1][0]]['createDate'])

    # list_top5 = sorted(dict_cluster.items(), key=lambda x: len(x[1]))[-5:]
    # # insert the top5 items into list_cluster, meanwhile delete the original item
    # for cluster_id, cluster_content in list_top5:
    #     for i in range(len(list_cluster)):
    #         if cluster_id == list_cluster[i][0]:
    #             del list_cluster[i]
    #             list_cluster.append((cluster_id, cluster_content))
    # list_cluster = list_cluster[:-5]

    # # resort the order, add new items emerged in the new time window
    # list_cluster_tmp = []
    # for cluster_id, _ in list_cluster:
    #     if cluster_id not in order_global:
    #         order_global.append(cluster_id)
    # for order_id in order_global:
    #     for cluster_id, cluster_content in list_cluster:
    #         if order_id == cluster_id:
    #             list_cluster_tmp.append((cluster_id, cluster_content))
    # list_cluster = list_cluster_tmp

    columns = ['source_id', 'title', 'summary', 'fetch_at', 'publish_at', 'source', 'source_url', 'info_sources', 'created_at']
    df_newslist = pd.DataFrame(columns=columns)
    for _, list_news in list_cluster:
        dict_onepiece = {}
        dict_onepiece['source_id'] = df_sql.iloc[list_news[0]]['id']
        dict_onepiece['title'] = df_sql.iloc[list_news[0]]['title']
        dict_onepiece['summary'] = df_sql.iloc[list_news[0]]['summary']
        dict_onepiece['fetch_at'] = pd.to_datetime(df_sql.iloc[list_news[0]]['createDate'], 'coerce')
        dict_onepiece['publish_at'] = pd.to_datetime(df_sql.iloc[list_news[0]]['publishDate'], 'coerce')
        dict_onepiece['source'] = df_sql.iloc[list_news[0]]['source']
        list_sources = [dict_onepiece['source']] # filter multiple docs from same source
        dict_onepiece['source_url'] = df_sql.iloc[list_news[0]]['sourceUrl']
        dict_onepiece['created_at'] = Timestamp('now')
        json_similar = []
        for news_similar in list_news[1:]: # if len() is only 1, this statement is also OK
            if df_sql.iloc[news_similar]['source'] not in list_sources:
                dict_similar = {}
                dict_similar['id'] = df_sql.iloc[news_similar]['id']
                dict_similar['title'] = df_sql.iloc[news_similar]['title']
                dict_similar['source'] = df_sql.iloc[news_similar]['source']
                dict_similar['sourceUrl'] = df_sql.iloc[news_similar]['sourceUrl']
                json_similar.append(dict_similar)
                list_sources.append(df_sql.iloc[news_similar]['source'])
        if not json_similar:
            dict_onepiece['info_sources'] = None
        else:
            dict_onepiece['info_sources'] = json.dumps(json_similar)
        df_newslist = df_newslist.append(dict_onepiece, ignore_index=True)

    print 'len of df_newslist is: {}'.format(len(df_newslist))

    # # this is for the top news
    # for _, list_news in list_top5:
    #     list_news = list_news[::-1] # inverse the list to make the create time inverse
    #     dict_onepiece = {}
    #     dict_onepiece['source_id'] = df_sql.iloc[list_news[0]]['id']
    #     dict_onepiece['title'] = u'今日热点：' + df_sql.iloc[list_news[0]]['title']
    #     dict_onepiece['summary'] = df_sql.iloc[list_news[0]]['summary']
    #     dict_onepiece['fetch_at'] = pd.to_datetime(df_sql.iloc[list_news[0]]['createDate'], 'coerce')
    #     dict_onepiece['publish_at'] = pd.to_datetime(df_sql.iloc[list_news[0]]['publishDate'], 'coerce')
    #     dict_onepiece['source'] = df_sql.iloc[list_news[0]]['source']
    #     list_sources = [dict_onepiece['source']] # filter multiple docs from same source
    #     dict_onepiece['source_url'] = df_sql.iloc[list_news[0]]['sourceUrl']
    #     dict_onepiece['created_at'] = Timestamp('now')
    #     json_similar = []
    #     for news_similar in list_news[1:]:
    #         if df_sql.iloc[news_similar]['source'] not in list_sources:
    #             dict_similar = {}
    #             dict_similar['id'] = df_sql.iloc[news_similar]['id']
    #             dict_similar['title'] = df_sql.iloc[news_similar]['title']
    #             dict_similar['source'] = df_sql.iloc[news_similar]['source']
    #             dict_similar['sourceUrl'] = df_sql.iloc[news_similar]['sourceUrl']
    #             json_similar.append(dict_similar)
    #             list_sources.append(df_sql.iloc[news_similar]['source'])
    #     if not json_similar:
    #         dict_onepiece['info_sources'] = None
    #     else:
    #         dict_onepiece['info_sources'] = json.dumps(json_similar)
    #     df_newslist = df_newslist.append(dict_onepiece, ignore_index=True)

    # local db
    # delete today's all the old news list
    while(True):
        try:
            local_con = MySQLdb.connect(host='192.168.200.100', port=3306, user='root', passwd='', db='dxydaily', charset='utf8')
        except MySQLdb.OperationalError, e:
            print 'MySQL Exception! Waiting for MySQL return to normal after 5 seconds ~'
            time.sleep(5)
            continue
        break
    local_cur = local_con.cursor()
    local_cur.execute('delete from articles where date(fetch_at) = %s', (date.today(),))
    local_con.commit()
    # write in the latest news list
    df_newslist.to_sql(name='articles', con=local_con, flavor='mysql', if_exists='append', index=False)

    # remote db for dxys
    # delete today's all the old news list
    while(True):
        try:
            dxys_con = MySQLdb.connect(host='192.168.200.209', port=3306, user='dxydaily', passwd='EDMH6XEmB4CwpPvHVugY', db='sync_dxydaily', charset='utf8')
        except MySQLdb.OperationalError, e:
            print 'MySQL Exception! Waiting for MySQL return to normal after 5 seconds ~'
            time.sleep(5)
            continue
        break
    dxys_cur = dxys_con.cursor()
    dxys_cur.execute('delete from articles where date(fetch_at) = %s', (date.today(),))
    dxys_con.commit()
    # write in the latest news list
    df_newslist.to_sql(name='articles', con=dxys_con, flavor='mysql', if_exists='append', index=False)

    print 'Job done at {}'.format(datetime.now())
    # the gabbage collector
    # this line is used to prevent memory accumulation and memory collapse
    gc.collect()

##########################################

schedule.every().day.at('01:00').do(job)
schedule.every().day.at('02:00').do(job)
schedule.every().day.at('03:00').do(job)
schedule.every().day.at('04:00').do(job)
schedule.every().day.at('05:00').do(job)
schedule.every().day.at('06:00').do(job)
schedule.every().day.at('07:00').do(job)
schedule.every().day.at('08:00').do(job)
schedule.every().day.at('09:00').do(job)
schedule.every().day.at('10:00').do(job)
schedule.every().day.at('11:00').do(job)
schedule.every().day.at('12:00').do(job)
schedule.every().day.at('13:00').do(job)
schedule.every().day.at('14:00').do(job)
schedule.every().day.at('15:00').do(job)
schedule.every().day.at('16:00').do(job)
schedule.every().day.at('17:00').do(job)
schedule.every().day.at('18:00').do(job)
schedule.every().day.at('19:00').do(job)
schedule.every().day.at('20:00').do(job)
schedule.every().day.at('21:00').do(job)
schedule.every().day.at('22:00').do(job)
schedule.every().day.at('23:00').do(job)
schedule.every().day.at('23:55').do(job)

while True:
    schedule.run_pending()
    time.sleep(60)

