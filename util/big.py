import pickle
import pandas as pd

import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

df3 = pd.read_html('https://gist.gith/ub.com/h3xx/1976236')
common_word = df3[0][1][26:].tolist()
tags = nltk.pos_tag(common_word)
print(tags)