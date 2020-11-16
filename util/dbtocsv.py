import pickle
import pandas as pd


def make_bot_name():
    df = pd.read_csv('bot5.csv')
    user_name = df['user_name']
    screen_name = df['screen_name']
    days = df['days']
    bot = df['bot']

    first_name = []
    last_name = []

    for s, d, b in zip(screen_name, days, bot):
        name = s.split(' ')
        if d < 1 and len(name) == 2 and b == 1:
            first_name.append(name[0]) if len(name[0]) > 3 else ''
            last_name.append(name[1]) if len(name[1]) > 3 else ''
            first_name = list(set(first_name))
            last_name = list(set(last_name))

    print(len(first_name))
    print(len(last_name))
    bot_names = {'first_name': first_name,
                 'last_name': last_name}

    with open('data/bot_names.pickle', 'wb') as pf:
        pickle.dump(bot_names, pf)
        # pickle.dump(last_name, pf)


def read():
    with open('data/bot_names.pickle', 'rb') as pf:
        x = pickle.load(pf)
        print(x['first_name'])
        print(x['last_name'])
