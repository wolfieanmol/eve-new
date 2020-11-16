from urllib.request import urlopen
from bs4 import BeautifulSoup
import shelve
import ast
import numpy as np
# from imdb import IMDb


ia = IMDb()


def by_category(category, url):
    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    h3 = soup.find_all('h3')
    h = h3[0:100]
    # print(h)
    s = [str(span.find('a')) for span in h]
    cleantext = BeautifulSoup(str(s), "lxml").get_text()
    cleaned = ast.literal_eval(cleantext)

    store(category, cleaned, 'imdb_database')

def store(category, li , file):
    with shelve.open(file) as f:
        if category not in f.keys():
            f[category] = li
        else:
            li_update = f[category]
            li_f = li_update + li
            f[category] = li_f


def read(category, file):
    with shelve.open(file) as f:
        # del f['top_250_movies']
        print([keys for keys in f.keys()])
        movies = f[category]
        return movies


# movie = ia.get_top250_movies()
# t = [str(m) for m in movie]
# store('top_250_movies', t)

# by_category('horror', 'https://www.imdb.com/list/ls003174642/?page=3')

# m = read('horror', 'imdb_database')
# print(m)
# print(len(m))
# n = [e for e in m if e != 'None']
# b = [e for e in n if e != ' \n\n\n']
# print((b))
# print(len(b))
# print(type(b))
# store('horror', b, 'imdb')
q = read('horror', 'imdb')
print(q)
print(len(q))

mv = [np.random.choice(q) for x in range(5)]
print(mv)
print('you can watch:\n{}\n{}\n{}\n{}\n{}'.format(mv[0], mv[1], mv[2], mv[3], mv[4]))
