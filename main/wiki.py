from main.database import Database
import threading
from threading import Thread, Timer
from main.Assistant import Assistant
import wikipedia
import nltk


class WikiStatus:
    def __init__(self, client):
        self.client = client

    def set_wiki_status(self, status, group_jid, peer_jid):
        message = Database("data.db").update_wiki_status(status, group_jid, peer_jid)
        if status == 'off' or status == 'temp':
            self.client.send_chat_message(group_jid,
                                          "Nerd mode turned off" if message is 1
                                          else "Nerd mode can only be turned off by an admin" if message is 2
                                          else "Nerd mode is already off" if message is 3
                                          else "Nice try Rage" if message is 4
                                          else "Nerd mode turned off for 60 minutes" if message is 5
                                          else "Nerd mode is already off")
        else:
            self.client.send_chat_message(group_jid,
                                          "Nerd mode turned on" if message is 1
                                          else "Nerd mode can only be turned on by an admin" if message is 2
                                          else "Nerd mode is already on" if message is 3
                                          else "Nice try Rage" if message is 4
                                          else "Nerd mode turned on" if message is 5
                                          else "Nerd mode is already on")

        if status == 'temp':
            status_thread = Timer(3600, self.status_timer, args=(group_jid, peer_jid))
            status_thread.start()

    def status_timer(self, group_jid, peer_jid):
        Database('data.db').update_wiki_status('on', group_jid, peer_jid)
        self.client.send_chat_message(group_jid, 'On again')


class Wiki:
    def __init__(self, client):
        self.client = client
        self.assistant = Assistant()

        self.legacy_wiki_list = []

        # with open('data/common_words.pickle', 'rb') as f:
        #     self.common_words = pickle.load(f)
        # with open('data/big.pickle', 'rb') as f:
        #     self.big = pickle.load(f)

    def wiki_thread_starter(self, group_jid, message):
        status = Database("data.db").get_wiki_status(group_jid)
        if status == 'on':
            t = Thread(target=self.wiki_threader, args=(message, group_jid))
            t.daemon = True
            t.start()

    def wiki_threader(self, message, group_jid):
        # print(threading.current_thread().name)
        query_list = self.assistant.wiki_info(message)

        q = [w for w in query_list if (group_jid, w) not in self.legacy_wiki_list]
        # print('q = ', q)
        if len(query_list) < 7:
            for query in q:
                wiki_thread = Thread(target=self.send_wiki_links, args=(query, group_jid),
                                     name='wiki_sub_thread')
                wiki_thread.start()

    def send_wiki_links(self, query, group_jid):
        # print(threading.current_thread().name)
        try:
            wiki_link = wikipedia.page(query).url
            wiki_summary = wikipedia.summary(query, sentences=1) if len(wikipedia.summary(query, sentences=1)) > 70 \
                else wikipedia.summary(query, sentences=2)
            search = str(wiki_link)[30:].lower().replace('_', ' ')
            lemma = nltk.stem.wordnet.WordNetLemmatizer()
            searched_query = lemma.lemmatize(search)
            # print(search)
            c = 0
            block = ['movie', 'film', 'tv', 'album', 'music', 'episode', 'artist', 'song', 'band', 'radio']
            for e in block:
                if e in wiki_summary.lower():
                    c += 1

            if (group_jid, wiki_link) not in self.legacy_wiki_list and (
                    query == search or query in wiki_summary.lower()) and c == 0:
                self.legacy_wiki_list.append((group_jid, wiki_link))

                # if query not in lis:
                self.wiki_list_creator(query)

                # print(wiki_link)
                # print('sending....')
                self.client.send_chat_message(group_jid, wiki_summary)
            # self.client.send_chat_message(group_jid, wiki_link)
            else:
                print('no link sent for:', query)
            # print(threading.current_thread().name, 'done')
        except:
            print(threading.current_thread().name, 'done with except')

    def wiki_list_creator(self, lis):
        # print('storing')
        with open('data/wikilist.txt', 'a+') as f:
            f.write(lis + '\n')
