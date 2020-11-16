import pickle
import pandas as pd

import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

adjectives = []
cuss = []
lis =[]
noun = []
dumb_noun =[]

# dumb nouns
with open('data/dumb_noun.txt','r') as f:
    for word in f:
        dumb_noun.append(word[:-1])
print('dumb_nouns:\n', dumb_noun[0:35])
print(len(dumb_noun))


# for abbrs
df1=pd.read_html('https://www.webopedia.com/quick_ref/textmessageabbreviations.asp')
# print(df1)
abbr_list = df1[0][0][1:].tolist()
abbv_list = [e.lower() for e in abbr_list]
print(abbr_list)
print(len(abbr_list))

# # common_english_words
with open('data/common_english_words', 'r') as f:
    for word in f:
        lis.append(word[:-1])

print(lis[0:10])
print(len(lis))
#
# # ##nouns
#
with open('data/nounlist_simple.txt','r') as f:
    for word in f:
        noun.append(word[:-1])
print(len(noun))
print(noun[0:20])
#
# adjectives
with open('data/adjectives.txt','r') as f:
    for word in f:
        adjectives.append(word[:-1])
print(adjectives[0:15])

# cities

s= 'Paris,London,Bangkok,Singapore,New York,Kuala Lumpur,Hong Kong,Dubai,Istanbul,Rome,Shanghai,Los Angeles,Las Vegas,Miami,Toronto,Barcelona,Amsterdam,Moscow,Vienna,Madrid,San Francisco,Vancouver,Budapest,Rio de Janeiro,Berlin,Tokyo,Mexico City,Seattle,Delhi,Sydney,Mumbai,Munich,Venice,Florence,Beijing,Cape Town,Washington D.C.Montreal,Atlanta,Boston,Philadelphia,Chicago,San Diego'
cities = s.split(',')
print("cities",len(cities))
#
#countries famous
c = 'Algeria,Angola,Argentina,Australia,Austria,Azerbaijan,Bahrain,Belarus,Bolivia,Brazil,Bulgaria,Canada,Chile,China,Colombia,Costa Rica,Croatia,Czech Republic,Denmark,Dominican Republic,Ecuador,Egypt,Finland,France,Germany,Ghana,Greece,Guatemala,Hungary,India,Indonesia,Iran,Ireland,Israel,Italy,Japan,Jordan,Kazakhstan,Kenya,Latvia,Lebanon,Luxembourg,Malaysia,Mexico,Morocco,Myanmar,Netherlands,New Zealand,Nigeria,Norway,Oman,Pakistan,Panama,Peru,Philippines,Poland,Portugal,Qatar,Romania,Russia,Saudi Arabia,Serbia,Singapore,Slovenia,South Africa,South Korea,Spain,Sri Lanka,Sweden,Switzerland,Thailand,Turkey,Ukraine,United Arab Emirates,United Kingdom,United States,Uruguay,Vietnam'

countries = c.lower().split(',')
print("countries", len(countries))
print(countries[0:15])


#animals

ani = 'Alpaca,Buffalo,Banteng,Cow,Cat,Chicken,Common,Camel,Donkey,Dog,Duck,Emu,Goat,GayalGoose,Horse,Honey Bee,Llama,Pig,Pigeon,Rhea,Rabbit,Sheep,Silkworm,Turkey,Yak,Zebu'
animals=ani.lower().split(',')

#names

df2 = pd.read_html('https://www.theguardian.com/news/datablog/2009/sep/08/baby-names-children-jack-olivia-mohammed')
girl_name = df2[0]['Name'][1:101].tolist()
boy_name = df2[1]['Name'][1:101].tolist()
nme = boy_name + girl_name
print(girl_name)
print(boy_name)
name = [w.lower() for w in nme]
print(name)
#
#
# 100 thousand common words
#
df3 = pd.read_html('https://gist.github.com/h3xx/1976236')
common_word = df3[0][1][26:].tolist()
lemma = nltk.stem.wordnet.WordNetLemmatizer()
lemmit_list = [lemma.lemmatize(element) for element in common_word if element is int]

#cuss words
with open('data/cuss.txt','r') as f:
    for string in f:
        cuss = string.split(', ')

        print("cuss:\n",cuss[0:15])
        print(len(cuss))


# # #dumping########
#
# l = abbv_list + name + adjectives + cuss + dumb_noun
l = common_word[:50000] + lis[:3000] + noun + animals + countries + cities
# #
with open('data/big.pickle', 'wb') as f:
    pickle.dump(l, f)
#
#
with open('data/big.pickle','rb') as f:
    las=pickle.load(f)
    print(len(las))

with open('data/common_words.pickle','rb') as f:
    los=pickle.load(f)
    print(len(los))

'''
trying to send only nouns in common words.
'''
#
# with open('data/big.pickle','rb') as f:
#     l = pickle.load(f)
#
# print(l[3700:3780])
# print(len(l))
# print(list(set(l)))
# print(len(list(set(l))))
# alpha_l = [x for x in l if not any(x1.isdigit() for x1 in x)]
# s =' '.join(word for word in alpha_l)
# print (s)
#
# tokens = nltk.word_tokenize(l)
# # print(tokens)
#
#
# tags = nltk.pos_tag(tokens)
#
# print(tags)
#
# noun_list = [element[0] for element in tags if element[1] == 'NN' or element[1] == 'NNS']
# print(noun_list)
# print(len(noun_list))











