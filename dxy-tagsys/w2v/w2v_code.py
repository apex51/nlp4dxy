import os
import gensim, logging

from datetime import datetime

sentence_dir = '/home/jiangh/result/result.corpus_drug_disease'
# result_dir = '/Users/jianghao/Desktop/models/'

start = datetime.now()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for line in open(self.dirname):
            yield line.split()

sentences = MySentences(sentence_dir)
model = gensim.models.Word2Vec(sentences, sg=1, hs=1, negative=0, sample=0.001)

model.save('w2v_model_sg_hs_size100_wd5_sp1e3')

print 'time duration for training gensim is {}'.format(datetime.now() - start)


############
# test code
############

with open('/Users/jianghao/Desktop/models/test_words.txt') as f:
    words = f.read().split()

output_result = ''
for word in words:
    output_result += (word + ':\n')
    try:
        for w, s in model.most_similar(word):
            output_result += (str(w) + ' ' + '{:.4}'.format(s) + ' ')
    except:
        output_result += '[warn] low frequency word'
    output_result += '\n\n'

with open('/Users/jianghao/Desktop/models/test_result.txt', 'wb') as f:
    f.write(output_result)

############
# code log
############

class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        '''
        iterate all the lines under dir './result'
        '''
        for item in os.listdir(self.dirname):
            os_path = os.path.join(self.dirname, item)
            print '{}'.format(os_path)
            if os.path.isdir(os_path):
                for fname in os.listdir(os_path):
                    print '>>> {}'.format(fname)
                    for line in open(os.path.join(os_path, fname)):
                        yield line.split()