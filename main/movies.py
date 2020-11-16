import shelve
import numpy as np


class Movies:
    def __init__(self):
        self.categories = {
            'comedy': self.get_movies('comedy'),
            'romcom': self.get_movies('romcom'),
            'romance': self.get_movies('romcom'),
            'action': self.get_movies('action'),
            'adventure': self.get_movies('action'),
            'action adventure': self.get_movies('action'),
            'family': self.get_movies('family'),
            'animated': self.get_movies('animated'),
            'latest': self.get_movies('new'),
            'new': self.get_movies('new'),
            'horror': self.get_movies('horror'),
            'top250': self.get_movies('top_250_movies'),
            'tv shows': self.get_movies('top_250_tv'),
            'tv series': self.get_movies('top_250_tv'),
            'web series': self.get_movies('top_250_tv'),
        }

    def get_movies(self, category):
        with shelve.open('imdb', writeback=True) as f:
            # print([keys for keys in f.keys()])
            movies = f[category]
            # print(movies)
            return movies

    def fetch_movies(self, message, group_jid):
        movies = None
        categories = ['comedy', 'romcom', 'romance', 'action', 'adventure', 'action adventure', 'family', 'animated',
                      'latest', 'new', 'horror', 'top 250', 'tv shows', 'tv series', 'web series']
        for category in categories:
            if category in message:
                movies = self.categories[category]
                break

        if movies is None:
            movies = self.categories['top250']
        if 'movies' in message:
            return [np.random.choice(movies) for x in range(5)]
        return np.random.choice(movies), category
