import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pickle


class Assistant(object):

    def __init__(self):
        self.ps = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def wiki_info(self, message):

        # message formatting. keeping only small alphabets and spaces.
        whitelist = set('abcdefghijklmnopqrstuvwxyz \n@#')
        string = message.lower()
        msg = ''.join(filter(whitelist.__contains__, string))

        # tokenizing
        tokens = nltk.word_tokenize(msg)

        # removing word starting with # or @
        call = [w for w in tokens if w[0] != '@' or w[0] != '#']

        # removing stop words.
        stop_list = []
        for w in call:
            if w not in self.stop_words:
                stop_list.append(w)
            else:
                stop_list.append('better')

        # lemming
        lemma = nltk.stem.wordnet.WordNetLemmatizer()
        lemmit_list = [lemma.lemmatize(element) for element in stop_list]

        # removing from 4500 words like names,cities,text_abbrs(very small lists of all)
        with open('data/common_words.pickle', 'rb') as f:
            l = pickle.load(f)

        common_word_list = []
        for w in lemmit_list:
            if w not in l:
                common_word_list.append(w)
            else:
                common_word_list.append('better')

        # tagging
        tags = nltk.pos_tag(common_word_list)

        # selecting only nouns and adjectives.
        noun_list = [element[0] for element in tags if element[1] == 'NN' or element[1] == 'NNS' or element[1] == 'JJ']
        # print(noun_list)

        # loading a long ass 100,000 list of most used english words and common farm animals,names,cities etc.
        with open('data/big.pickle', 'rb') as f:
            big = pickle.load(f)

        # removing common words.
        big_list = [word for word in noun_list if word not in big]

        # creating sequential permutations of all targeted words that occur together in tags
        i = 0
        s = ''
        while i < len(tags):
            if tags[i][1] == 'NN' or tags[i][1] == 'NNS' or tags[i][1] == 'JJ':
                if s == '':
                    s += tags[i][0]
                else:
                    s = s + ' ' + tags[i][0]
                    big_list.append(s)
                    i -= 1
                    s = ''
            else:
                s = ''

            i += 1

        # removing recorded false words
        blacklist = []
        with open('data/wikilist.txt', 'r') as f:
            for word in f:
                blacklist.append(word[:-1])
        black = [w for w in big_list if w not in blacklist]

        # removing repetitions fronm the list
        final_list = list(set(black))
        return final_list
