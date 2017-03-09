import re
import jieba

# replace [.*] with ' '
re.sub(r'\[.+?\]', ' ', s)

# replace url with ' '
re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', ' ', s_new)
# a simple url cleaner
re.sub(r'(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/.]|[~]|[:?=&_])*', ' ', s)

# replace email with ' '
re.sub(r'[\w\.-]+@[\w\.-]+', ' ', s_tmp)

# break sentences, remove extra \n, remove spaces followed by \n
re.sub(r'(。+)|(？+)', '\n', line)
re.sub(r'\n\n+', '\n', line)
re.sub(r' +\n', '', line)

# code samples for command lines
output_lines = ''
with open('/Users/jianghao/Desktop/content/bbs/000000_0') as f:
    for line in f.readlines():
        line = re.sub(r'\[.+?\]', ' ', line)
        line = re.sub(r'(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/.]|[~]|[%?=&_:-])*', ' ', line)
        line = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', line)
        line = re.sub(r'(。+)|(？+)', '\n', line)
        line = re.sub(r'\n\n+', '\n', line)
        line = re.sub(r' +\n', '', line)
        line = ' '.join(jieba.cut(line))
        output_lines += line

with open('/Users/jianghao/Desktop/test.txt', 'wb') as f:
    f.write(output_lines)

line = line.decode('utf8')
re.sub(u'([^\u03B1-\u03C9\u4E00-\u9FA5a-zA-Z0-9+_\n]+)',' ', s)

# load use define dict
jieba.load_userdict('/Users/jianghao/Desktop/content/dic/med_dxy.dic')

# filter strange notations
re.sub('&nbsp', ' ', s)
# all words start with chinese, english or number, so filter the other
re.sub(u'( [^\u03B1-\u03C9\u4E00-\u9FA5a-zA-Z0-9\n])', ' ', s.decode('utf8'))
# replace one char and all numbers, first add extra to both side, after done replace all redundancy
re.sub('  ', ' ', s)
re.sub(u' [a-zA-Z] ', ' ', s)
re.sub(u' \d+\.*\d* ', ' ', s)
re.sub(u'[ ]+', ' ', s)
# other characters
#  　 。   ） （ Ⅸ  ／ ． ‐   ― — Ⅺ ’  ； ： ” “ С   Ｃ Ｂ  … ) ( + / . °  ′ :  < ? >  《 ≈ －   Ⅶ ｜ _ ～ Ⅱ Ⅰ Ⅳ Ⅲ Ⅵ Ⅴ Ⅷ 䗪 é è Ⅻ = Δ 䓬 Ｋ ⅱ Ⅹ ２ ぱ  ö ü  

import glob
for file_path in glob.glob('~~~~'):
    pass
    filename = file_path.split('/')[-1]
    write('~{}'.format(filename))


#############################
## code for cms cleansing
#############################

jieba.load_userdict('/home/jianghao/content/dic/med_dxy.dic')
jieba.enable_parallel(4)

with open('/Users/jianghao/Desktop/hive/cms/000000_0') as f:
    lines = f.read()
# cleasing &x; html code
# first iterate &abc; to character
with open('/Users/jianghao/Desktop/seg/character_map') as f:
    character_map = f.readlines()
for character_item in character_map:
    character_item = re.split('[ ]+', character_item)
    character, code = character_item[0], character_item[2]
    lines = re.sub(code, character, lines)
# then iterate $#123; to character
with open('/Users/jianghao/Desktop/seg/character_map') as f:
    character_map = f.readlines()
for character_item in character_map:
    character_item = re.split('[ ]+', character_item)
    character, code = character_item[0], character_item[1]
    lines = re.sub(code, character, lines)
# cleasing CJK Compatibility Ideograph html code to simplified chinese
with open('/Users/jianghao/Desktop/seg/cjk_map') as f:
    cjk_map = f.readlines()
for cjk_item in cjk_map:
    cjk_item = re.split('[ ]+', cjk_item)
    character, code = cjk_item[0], cjk_item[2]
    lines = re.sub('&#'+code+';', character, lines)
# &nbsp; is white space, which should do seperately
lines = re.sub(r'&nbsp;', ' ', lines) 
lines = re.sub(r'<.+?>', ' ', lines)
lines = re.sub(r'(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/\.]|[~]|[%?=&_;:-])+', ' ', lines)
lines = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', lines) 
lines = re.sub(r'\x01', '\n', lines) # sub ^A
lines = re.sub(r'(。+)|(？+)', '\n', lines)
lines = ' '.join(jieba.cut(lines))
lines = re.sub(' ', '  ', lines)
lines = re.sub(u' [^\u03B1-\u03C9\u4E00-\u9FA5a-zA-Z0-9 \n]+ ', ' ', lines)
lines = re.sub(u' [a-zA-Z] ', ' ', lines)
lines = re.sub(u' \d+\.*\d* ', ' ', lines)
lines = re.sub(u'[ ]+', ' ', lines)
lines = re.sub(r'\n[ \n]+\n', '\n', lines)
lines = re.sub(r' \n ', '\n', lines)
lines = lines.lower()
with open('/Users/jianghao/Desktop/test.txt', 'wb') as f:
    f.write(lines.encode('utf8'))

#############################
## code for disease cleansing
#############################

with open('/Users/jianghao/Desktop/train.txt') as f:
    lines = f.read()
lines = re.sub(r'&nbsp;', ' ', lines) 
lines = re.sub(r'<sub>(.*?)</sub>', r'\1', lines)
lines = re.sub(r'<sup>(.*?)</sup>', r'\1', lines)
lines = re.sub(r'\x01', '\n', lines) # sub ^A
lines = re.sub(r'(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/\.]|[~]|[%?=&_;:-])+', ' ', lines)
lines = re.sub(r'<.+?>', ' ', lines)
lines = re.sub(r'(。+)|(？+)|(；+)', '\n', lines)

lines = ' '.join(jieba.cut(lines))

lines = re.sub(' ', '  ', lines)
lines = re.sub(u' [^\u03B1-\u03C9\u4E00-\u9FA5a-zA-Z0-9 \n]+ ', ' ', lines)
lines = re.sub(u' [a-zA-Z] ', ' ', lines)
lines = re.sub(u' \d+\.*\d* ', ' ', lines)
lines = re.sub(u'[ ]+', ' ', lines)
lines = re.sub(r'\n[ \n]+\n', '\n', lines)
lines = re.sub(r' \n ', '\n', lines)

lines = lines.lower()


# match a tag in a elegent way
re.sub(r'(?P<tag>(<sub>)|(<sup>)|(SUB)|(SUP))(?P<content>.*?)(?P=tag)', '\g<content>', '<sub>3<SUB>')