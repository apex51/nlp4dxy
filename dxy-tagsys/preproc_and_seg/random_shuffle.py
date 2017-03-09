'''
- create a file to store all corpus
- first random shuffle weixin, cms, drugs, disease
- then random pick a bbs file, shuffle inside
- write append each time to the unified corpus
'''

import os
import random

corpus_path = '/Users/jianghao/Desktop/result/'
result_path = '/Users/jianghao/Desktop/result/result.corpus'

lines = []
for item in os.listdir(corpus_path):
    if item in ['cms', 'disease', 'drugs', 'weixin']:
        os_path = os.path.join(corpus_path, item)
        for fname in os.listdir(os_path):
            with open(os.path.join(os_path, fname)) as f:
                lines += f.readlines()

random.shuffle(lines)

with open(result_path, 'wb') as f:
    f.write(lines)

# deal with bbs data
os_path = os.path.join(corpus_path + 'bbs')
bbs_files = os.listdir(os_path)
random.shuffle(bbs_files)
for fname in bbs_files:
    print 'dealing with {}'.format(fname)
    with open(os.path.join(os_path, fname)) as f:
        lines = f.readlines()
        random.shuffle(lines)
        with open(result_path, 'a') as fw:
            fw.write(''.join(lines))