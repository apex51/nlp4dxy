# -*- coding: utf-8 -*-

'''
1.filter and keep every in-dic words
2.word expansion
3.clustering
'''

import re
import numpy as np
import gensim, logging
import sklearn.cluster as clstr
import pickle

model = gensim.models.Word2Vec.load('/Users/jianghao/Desktop/models/w2v_model_sg_hs_size400_wd6_mc5_sp1e5/w2v_model_sg_hs_size400_wd6_mc5_sp1e5')
cluster = clstr.KMeans(n_clusters=10)
words = []
dic_centroids = {}

# output each cluster's centroid vec, most similar word and word list
def output_cluster():
    global words
    global cluster
    global model

    output = ''
    for cluster_id in range(cluster.cluster_centers_.shape[0]):
        center_word, center_confidence = model.most_similar([cluster.cluster_centers_[cluster_id]], topn=1)[0]
        labels = cluster.labels_
        cluster_words = [words[i] for i in range(len(words)) if labels[i] == cluster_id]
        output += ('cluster id:' + str(cluster_id) + '\n')
        output += ('center_word:' + center_word + ' confidence: ' + str(center_confidence) + '\n')
        output += ('words in this cluster:\n')
        output += (' '.join(cluster_words) + '\n\n')

    with open('/Users/jianghao/Desktop/seed/output.txt', 'wb') as f:
        f.write(output)

# convenient func: preprocessing
def read_and_train():
    global words
    global cluster
    global model

    with open('/Users/jianghao/Desktop/seed/seeds.txt') as f:
        words = f.read()
    words = re.split(u'[，、]', words.decode('utf8'))
    words_in_dic = []
    for word in words:
        word = word.encode('utf8').lower()
        if word in model.vocab:
            words_in_dic.append(word)
    words_in_dic = [word for word in set(words_in_dic)]
    print '{} original words, {} words left.'.format(len(words), len(words_in_dic))

    with open('/Users/jianghao/Desktop/seed/seeds.txt', 'wb') as f:
        f.write('、'.join(words_in_dic))

    # expansion and clustering
    # option 1, find n words for each seed, then do the clustering
    # option 2, find words that is x-distance from each seed, then do the clustering
    # problem, what kind of clustering?

    # expansion: this step is bit slow
    words = []
    for word in words_in_dic:
        word_list = [item[0] for item in model.most_similar(word, topn=150) if item[1] >= 0.6]
        words.extend(word_list)
    words = [word for word in set(words)]

    # vectorization: this step is bit slow
    word_vecs = np.array([model[word] for word in words]).astype(np.float32)

    # training
    cluster.fit(word_vecs)
    output_cluster()

# convenient func: del_cluster()
def del_cluster(cluster_index):
    global words
    global cluster
    global model

    words_opr = words
    labels = cluster.labels_
    for word in [words[i] for i in range(len(words)) if labels[i] == cluster_index]:
        words_opr.remove(word)
    words = words_opr
    word_vecs = np.array([model[word] for word in words_opr]).astype(np.float32)
    cluster.fit(word_vecs)
    output_cluster()

# convenient func: get_centroid()
def get_centroid(label_name):
    global words
    global cluster
    global model
    global dic_centroids

    output = ''
    for cluster_id in range(cluster.cluster_centers_.shape[0]):
        center_word, center_confidence = model.most_similar([cluster.cluster_centers_[cluster_id]], topn=1)[0]
        labels = cluster.labels_
        cluster_words = [words[i] for i in range(len(words)) if labels[i] == cluster_id]
        output += ('cluster id:' + str(cluster_id) + '\n')
        output += ('center_word:' + center_word + ' confidence: ' + str(center_confidence) + '\n')
        output += ('words in this cluster:\n')
        output += (' '.join(cluster_words) + '\n\n')

    with open('/Users/jianghao/Desktop/seed/centroid/{}.txt'.format(label_name), 'wb') as f:
        f.write(output)

    dic_centroids[label_name] = cluster.cluster_centers_

# centroids = []
# labels = []

print '\n'.join([item[0] + ' ' + str(item[1]) for item in model.most_similar('曲奇')])
positive=['woman', 'king'], negative=['man'], topn=1

