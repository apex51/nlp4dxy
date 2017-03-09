# -*- coding: utf-8 -*-
# Author: Jiang Hao <jiangh@dxy.cn>

import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt

from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc

FILE_PATH = '/Users/jianghao/Projects/daily/'

# load from pkl generated from preprocess.py
with open(FILE_PATH + 'pickled data/data_set.pkl', 'rb') as f:
    df_source = pickle.load(f)

# make ready positive and negative cases
negative_rows = random.sample(df_source[df_source['flag'] == 0].index, 8000)
positive_rows = random.sample(df_source[df_source['flag'] == 1].index, 8000)
rows = negative_rows + positive_rows
df_dataset = df_source.ix[rows]

# train test split
sss = StratifiedShuffleSplit(dataset['flag'], 1, test_size=0.5, random_state=22)
train_index, test_index = [(a, b) for a, b in sss][0]
df_train = dataset.iloc[train_index]
df_test = dataset.iloc[test_index]

# transform to tfidf features
vectorizer = TfidfVectorizer(encoding='utf8')
x_train = vectorizer.fit_transform(df_train['content'])
y_train = df_train['flag']
x_test = vectorizer.transform(df_test['content'])
y_test = df_test['flag']

# training and predicting
clf = SGDClassifier(loss='log', penalty='l2', n_iter=50, alpha=0.00001, fit_intercept=True)
clf.fit(x_train, y_train)
pred = clf.predict(x_test)

# training statistics
print classification_report(y_test, pred)
cm = confusion_matrix(y_test, pred)
print cm
plt.matshow(cm)
plt.colorbar()

# Compute ROC curve and ROC area for each class
fpr, tpr, threshold = roc_curve(y_test, pred[:,1])
roc_auc = auc(fpr, tpr)
print roc_auc

# Plot of a ROC curve for a specific class
plt.figure()
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()