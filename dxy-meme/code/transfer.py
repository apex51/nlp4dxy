import pandas as pd
import numpy as np
import MySQLdb
from pandas.tslib import Timestamp
import pickle


local_con = MySQLdb.connect(host='192.168.200.100', port=3306, user='root', passwd='', db='dxydaily', charset='utf8')
remote_con = MySQLdb.connect(host='192.168.200.208', port=3306, user='ruby_daily', passwd='dLhQjH2tyhGZLHxCRMq3', db='infocrawl', charset='utf8')
df_sql = pd.read_sql('select id, title, summary, content, createDate, publishDate, source, sourceUrl from info_push_source where createDate between \'2015-11-20\' and \'2015-11-25\'', con=remote_con)
# after filtering, write to mysql
# column_map = {'id': 'source_id', 'createDate': 'fetch_at', 'publishDate': 'publish_at', 'sourceUrl': 'source_url'}
# df_sql.rename(columns=column_map, inplace=True)
# df_sql.drop('content', axis=1, inplace=True)
# # deal with time
# df_sql['created_at'] = Timestamp('now')
# df_sql['fetch_at'] = pd.to_datetime(df_sql['fetch_at'], 'coerce')
# df_sql['publish_at'] = pd.to_datetime(df_sql['publish_at'], 'coerce')
# df_sql.to_sql(name='articles', con=local_con, flavor='mysql', if_exists='append', index=False)

with open('../data/news_20151120_20151125.txt', 'wb') as f:
    f.writelines(['\t'.join([str(int(df_sql.loc[index]['id'])), df_sql.loc[index]['title'], df_sql.loc[index]['content']]) for index in df_sql.index])

# with open('../data/df_sql_1109.pkl', 'wb') as f:
#     pickle.dump(df_sql, f)