from typing import Union
import kik_unofficial.datatypes.xmpp.chatting as chatting
from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback
from kik_unofficial.datatypes.xmpp.errors import SignUpError, LoginError
from kik_unofficial.datatypes.xmpp.roster import PeersInfoResponse
from kik_unofficial.datatypes.xmpp.sign_up import RegisterResponse, UsernameUniquenessResponse
from kik_unofficial.datatypes.xmpp.login import LoginResponse, ConnectionFailedResponse
from kik_unofficial.datatypes.xmpp.xiphias import UsersResponse, UsersByAliasResponse

import sys
import ast
from threading import Thread
import time
import wikipedia
import numpy as np
import random
import re
import nltk
import colorama
import logging

from main.database import Database
from main.databse_updater import DatabaseUpdate
from main.verify import VerifyStatus, Verify
from main.wiki import WikiStatus, Wiki
from main.movies import Movies
import main.mongo as mongo
from main.dialogues import Dialogues
import main.bot_config as BotConfig


def main():
    bot = EveBot()


class EveBot(KikClientCallback):
    def __init__(self):
        bot_configuration = BotConfig.get_bot("eve_assist_1000")
        self.client = KikClient(self,
                                kik_username=bot_configuration[0].username,
                                kik_password=bot_configuration[0].password,
                                device_id_override=bot_configuration[0].device_id,
                                android_id_override=bot_configuration[0].android_id,
                                operator_override=bot_configuration[0].operator,
                                brand_override=bot_configuration[0].brand,
                                model_override=bot_configuration[0].model,
                                android_sdk_override=bot_configuration[0].android_sdk,
                                install_date_override=bot_configuration[0].install_date,
                                logins_since_install_override=bot_configuration[0].logins_since_install,
                                registrations_since_install_override=bot_configuration[0].registrations_since_install)
        self.buffer = []
        # for captcha eval
        self.verify = Verify(self.client)

        self.databaseUpdate = DatabaseUpdate(self.client)
        self.mongo = mongo.MongoDatabase()
        self.dialogues = Dialogues(self.client)

        self.bot_info = {}

        self.t = 0
        self.lock = 0

        self.veri_queue = []

        self.owner = []

    def bot_detect(self):
        # TODO check if using simple list queue leads to thread collisions (from joining thread and when all info is
        #  collected thread)
        # Do not change this method.

        # resolving possible starvation by emptying queue after max size.
        if len(self.veri_queue) > 3:
            self.veri_queue = []
            self.bot_info = {}
            self.lock = 0

        # group_jid and peer_jid are certain to be present in non empty bot_info. Resetting if that is not the case.
        if ('group_jid' not in self.bot_info or 'peer_jid' not in self.bot_info) and len(self.bot_info) != 0:
            self.bot_info = {}
            self.lock = 0

        # lock ensures 2 threads don't access same data.
        # (can be caused by joining peer thread and verification of previous peer done thread together)
        if len(self.veri_queue) > 0 and len(self.bot_info) == 0 and self.lock == 0:
            self.lock = 1
            self.bot_info['group_jid'] = self.veri_queue[0][0]
            self.bot_info['peer_jid'] = self.veri_queue[0][1]
            self.client.add_friend(self.bot_info['peer_jid'])  # request for username and screen name
            self.client.xiphias_get_users_by_alias(self.bot_info['peer_jid'])  # request for no. of days

        if len(self.bot_info) == 5:
            try:
                self.verify.bot(self.bot_info)
            finally:
                self.bot_info = {}
                self.veri_queue.pop(0)
                self.lock = 0
                Thread(target=self.bot_detect, args=()).start()

    def on_authenticated(self):
        print("Now I'm Authenticated, let's request roster")
        # self.client.request_roster()

    def on_login_ended(self, response: LoginResponse):
        print("Full name: {} {}".format(response.first_name, response.last_name))

    def on_chat_message_received(self, chat_message: chatting.IncomingChatMessage):
        s = chat_message.body.lower()

        if chat_message.from_jid == 'suckawolf_ggv@talk.kik.com' and 'broadcast' in s:
            m = s.split("broadcast ")[1].split("link: ")[0]
            l = chat_message.body.split("link: ")[1] if len(s.split("link: ")) > 1 else None
            self.client.send_chat_message(chat_message.from_jid, m)
            self.client.send_chat_message(chat_message.from_jid, l)
            Thread(target=self.broadcast, args=(m, l)).start()

        if s == 'hey':
            self.client.send_chat_message(chat_message.from_jid, "Hello {}".format(chat_message.from_jid)[0:-17])

        elif s == 'help':
            self.client.send_chat_message(chat_message.from_jid, "EVE 2.0")
            with open("texts/help.txt", "r") as f:
                help_ = f.read()
                self.client.send_chat_message(chat_message.from_jid, help_)

            self.client.send_chat_message(chat_message.from_jid,
                                          'contact me for help @suckawolf or join #eve_support')
        elif s == 'donate':
            self.client.send_chat_message(chat_message.from_jid,
                                          "Thanks for using Eve! Please consider donating to help Eve grow and running.")
            self.client.send_link(chat_message.from_jid, "https://www.paypal.me/wolfieeve", "Tap here to donate on "
                                                                                            "paypal.")

        elif s == 'friend':
            self.client.send_chat_message(chat_message.from_jid,
                                          "Yay, we're friends now! You can now add me to any group")
            self.client.add_friend(chat_message.from_jid)

        elif s == 'faq':
            with open("texts/faq.txt") as f:
                faq = f.read()
                self.client.send_chat_message(chat_message.from_jid, faq)

        elif s == 'update':
            with open("texts/update.txt") as f:
                update = f.read()
                self.client.send_chat_message(chat_message.from_jid, update)

        else:
            self.client.send_chat_message(chat_message.from_jid,
                                          "say help to see commands, friend to be able to add me to your group, "
                                          "faq for frequently asked questions, update to see info new features")

    def broadcast(self, message, lin):
        jid = Database("data.db").get_all_groups()
        for j in jid:
            print(colorama.Fore.BLUE + "BROADCASTING")
            try:
                self.client.send_chat_message(j + "@groups.kik.com", message)
                self.client.send_link(j + "@groups.kik.com", link=lin, title="Survey") if lin is not None else None
                rt = random.randrange(5, 10)
                time.sleep(rt)
            except():
                print(colorama.Fore.BLUE + "not found")

    def on_message_delivered(self, response: chatting.IncomingMessageDeliveredEvent):
        print("[+] Chat message with ID {} is delivered.".format(response.message_id))

    def on_message_read(self, response: chatting.IncomingMessageReadEvent):
        print("[+] Human has read the message with ID {}.".format(response.message_id))

    def on_group_message_received(self, chat_message: chatting.IncomingGroupChatMessage):
        s = chat_message.body.lower()

        # --------------------------
        #  Captcha Eval
        # -------------------------

        # TODO optimize it, no need to create an evaluation thread for every single message sent. (although no
        #  performance issues noticed)
        self.verify.eval_message(chat_message.from_jid, chat_message.group_jid,
                                 chat_message.body)

        # --------------------------
        #  Verification status
        # -------------------------

        if s == "eve stop verification":  # admin
            print(1)
            VerifyStatus(self.client).set_verification_status("off", chat_message.group_jid,
                                                              chat_message.from_jid)

        elif s == "eve start verification":  # admin
            print(2)
            VerifyStatus(self.client).set_verification_status("on", chat_message.group_jid,
                                                              chat_message.from_jid)

        elif "eve set verification time to" in s:  # admin
            try:
                ti = int(s.split("eve set verification time to ")[1]) * 60
                VerifyStatus(self.client).set_verification_time(ti, chat_message.group_jid, chat_message.from_jid)
            except Exception:
                self.client.send_chat_message(chat_message.group_jid, "give only a number after command\n"
                                                                      "example: eve set verification time to 5")

        elif "eve set verification days to" in s:  # admin
            try:
                d = int(s.split("eve set verification days to ")[1])
                VerifyStatus(self.client).set_verification_days(d, chat_message.group_jid, chat_message.from_jid)
            except Exception:
                self.client.send_chat_message(chat_message.group_jid, "give only a number after command\n"
                                                                      "example: eve set verification days to 5")

        elif s == "eve verification time left":  # user
            t = Database('data.db').get_join_time(chat_message.group_jid)
            if time.time() - t > 43200:
                self.client.send_chat_message(chat_message.group_jid, "I can verify now")
            else:
                time_left = 43200 - (time.time() - t)
                hours = time_left // 3600
                minutes = (time_left - hours * 3600) // 60
                self.client.send_chat_message(chat_message.group_jid,
                                              "Captcha verification will start after : "
                                              "{} hours and {} minutes".format(hours, minutes))

        elif "eve set welcome message to " in s:  # admin
            welcome_msg = chat_message.body.split("Eve set welcome message to ")[1]
            DatabaseUpdate(self.client).welcome_message(welcome_msg, chat_message.group_jid,
                                                        chat_message.from_jid)

        # --------------------------
        #  Wiki status
        # -------------------------

        elif s == "eve stop forever":  # admin
            WikiStatus(self.client).set_wiki_status('off', chat_message.group_jid, chat_message.from_jid)

        elif s == "eve start":
            WikiStatus(self.client).set_wiki_status('on', chat_message.group_jid, chat_message.from_jid)

        elif s == "eve stop":
            WikiStatus(self.client).set_wiki_status('temp', chat_message.group_jid, chat_message.from_jid)

        # --------------------------
        #  given name
        # -------------------------

        elif "eve call me" in s:
            name = chat_message.body.split('Eve call me ')[1]
            self.client.send_chat_message(chat_message.group_jid, "Ok, {}".format(name))
            Database("data.db").given_name(name, chat_message.group_jid, chat_message.from_jid)

        elif "eve forget my name" in s:
            # TODO this does not work :(
            Database("data.db").delete_given_name(chat_message.group_jid, chat_message.from_jid)
            self.client.send_chat_message(chat_message.group_jid, "Your name has been forgotten")

        elif s == 'hey' or s == 'hey eve':
            name = Database("data.db").get_given_name(chat_message.group_jid, chat_message.from_jid)
            name = '' if name is None else name
            self.client.send_chat_message(chat_message.group_jid, "Hello {}".format(name))

        # -------------------------
        #  misc
        # -------------------------

        elif s == 'eve leave':  # admin
            admins = ast.literal_eval(Database("data.db").get_admins(chat_message.group_jid))
            print(admins)
            for key in admins.keys():
                print(key)
                if key == chat_message.from_jid and admins[key] != 'Rage bot':
                    self.databaseUpdate.delete_group_info(chat_message.group_jid)
                    self.client.leave_group(chat_message.group_jid)
                    break
        #          if admins[key] == 'Rage bot':
        #             self.client.send_chat_message(chat_message.group_jid, "I ain't leaving Rage")
        #            break

        elif s == 'eve':
            self.client.send_chat_message(chat_message.group_jid, 'Hello I\'m Eve. You called?')

        elif 'eve' in s and 'hug' in s:
            reply = np.random.choice([0, 1, 2, 3])
            if reply == 0:
                self.client.send_chat_message(chat_message.group_jid, 'sure pay me 10 shmekles first')
                self.client.send_chat_message(chat_message.group_jid, 'nah, I\'m just kidding.\n'
                                                                      'I give hugs for free. *hugs*')
            elif reply == 1:
                self.client.send_chat_message(chat_message.group_jid, 'sure! *hugs*')

            elif reply == 2:
                self.client.send_chat_message(chat_message.group_jid, 'One hug coming right up')
                self.client.send_chat_message(chat_message.group_jid, '*big hug* 😀')
            else:
                self.client.send_chat_message(chat_message.group_jid, '*hugs* 😊')

        elif s == 'eve toss a coin':
            print(14)
            outcome = random.choice([0, 1])
            self.client.send_chat_message(chat_message.group_jid, 'It\'s a head' if outcome == 1 else 'It\'s a tail')

        elif 'eve' in s and ' or ' in s and len(s) < 100:
            print(15)
            yo = re.findall('\\b' + 'eve' + '\\b', chat_message.body, flags=re.IGNORECASE)
            if yo != []:
                tokens = nltk.word_tokenize(s)
                for i in range(len(tokens)):
                    if tokens[i] == 'or':
                        out1 = str(tokens[i - 1])
                        out2 = str(tokens[i + 1])
                        if out1 == 'me':
                            out1 = 'you'
                        if out2 == 'me':
                            out2 = 'you'

                        outcome = random.choice([0, 1])
                        self.client.send_chat_message(chat_message.group_jid, out1 if outcome == 1 else out2)

        elif s == 'eve who is your dad' or s == 'eve who made you':
            print(16)
            self.client.send_chat_message(chat_message.group_jid,
                                          'I was created by Wolfie.\nYou can contact him at: @suckawolf')

        # --------------------------
        #  movies
        # -------------------------

        elif "movies" in s and "eve " in s:
            print(7)
            mv = Movies().fetch_movies(s, chat_message.group_jid)
            self.client.send_chat_message(chat_message.group_jid,
                                          f'you can watch:\n{mv[0]}\n{mv[1]}\n{mv[2]}\n{mv[3]}\n{mv[4]}')
        elif "movie" in s and "eve " in s:
            print(8)
            mv = Movies().fetch_movies(s, chat_message.group_jid)
            self.client.send_chat_message(chat_message.group_jid,
                                          f'I hear {mv[0]} is a good {"" if mv[1] == "web series" else mv[1]} movie')

        # --------------------------
        #  Wiki answers
        # -------------------------

        elif "eve what is" in s or "eve who is" in s or "eve where is" in s or "eve what are" in s \
                or "eve who are" in s or "eve where are" in s or "eve what's" in s:

            t = Thread(target=self.wiki_manual, args=(chat_message.group_jid, chat_message.body))
            t.start()

        # else:
        #     Wiki(self.client).wiki_thread_starter(chat_message.group_jid, chat_message.body)

        # --------------------------
        #  Substitutions
        # -------------------------
        elif " > " in chat_message.body:
            sub = chat_message.body.split(" > ")
            group = self.mongo.find_by_jid(chat_message.group_jid)
            self.dialogues.save_dialogue(sub, group, chat_message.group_jid)

        elif " >> " in chat_message.body:
            sub = chat_message.body.split(" >> ")
            admins = ast.literal_eval(Database("data.db").get_admins(chat_message.group_jid))
            admins = list(admins.keys())
            if chat_message.from_jid in admins:
                group = self.mongo.find_by_jid(chat_message.group_jid)
                self.dialogues.save_admin_dialogue(sub, group, chat_message.group_jid)
            else:
                self.client.send_chat_message(chat_message.group_jid, "This can only be done by an admin")

        elif " >>> " in chat_message.body:
            sub = chat_message.body.split(" >>> ")
            group = self.mongo.find_by_jid(chat_message.group_jid)
            self.dialogues.save_user_dialogue(sub, group, chat_message.group_jid, chat_message.from_jid)

        elif "eve delete" in s:
            key = s.split["eve delete "][0]

            substitution = self.mongo.find_by_jid(chat_message.group_jid).substitutions.filter(key=key,
                                                                                               user_jid=chat_message.from_jid)
            print(chat_message.from_jid)
            if len(substitution) != 0:
                print("123")
                substitution.delete()
            else:
                substitution = self.mongo.find_by_jid(chat_message.group_jid).substitutions.filter(
                    key=chat_message.body, user_jid=None)
                if len(substitution) != 0:
                    self.client.send_chat_message(chat_message.group_jid, substitution[0].value)


        else:
            substitution = self.mongo.find_by_jid(chat_message.group_jid).substitutions.filter(key=chat_message.body,
                                                                                               user_jid=chat_message.from_jid)
            print(chat_message.from_jid)
            if len(substitution) != 0:
                print("123")
                self.client.send_chat_message(chat_message.group_jid, substitution[0].value)
            else:
                substitution = self.mongo.find_by_jid(chat_message.group_jid).substitutions.filter(
                    key=chat_message.body, user_jid=None)
                if len(substitution) != 0:
                    self.client.send_chat_message(chat_message.group_jid, substitution[0].value)

    def wiki_manual(self, group_jid, body):
        qu = ' '.join(body.split()[3:])
        try:
            ans = wikipedia.summary(qu, sentences=1)
            self.client.send_chat_message(group_jid, ans)
        except Exception:
            self.client.send_chat_message(group_jid,
                                          'sorry too many articles found. Be more specific.')

    def on_friend_attribution(self, response: chatting.IncomingFriendAttribution):
        # self.client.send_chat_message(response.referrer_jid,
        #                               "Hey there!\n say help to see commands\nsay friend to add me to any group")
        print("[+] Friend attribution request from " + response.referrer_jid)

    def on_image_received(self, image_message: chatting.IncomingImageMessage):
        print("[+] Image message {} was received from {}".format(image_message.image_url, image_message.from_jid))

    def on_xiphias_get_users_response(self, response: Union[UsersResponse, UsersByAliasResponse]):
        days = (time.time() - response.days[0]) / 86400
        print(days)
        self.bot_info['days'] = days

        if len(self.bot_info) == 5:
            try:
                self.verify.bot(self.bot_info)
            finally:
                self.bot_info = {}
                self.veri_queue.pop(0)
                self.lock = 0
                Thread(target=self.bot_detect, args=()).start()
        # if days < 3:
        #     self.bot_info.append(days)

        # if len(self.bot_info) == 2:
        #     selself.bot_info.append(days)f.bot_info.append(days)
        # else:
        #     self.bot_info = []

    def on_peer_info_received(self, response: PeersInfoResponse):
        print(colorama.Fore.GREEN + "[+] Peer info: " + str(response.u))
        print('\033[39m')

        if len(response.users) == 0:
            # sometimes the peer info is returned empty. To avoid starvation; bad info is removed without
            # verification from the queue and every other param are reset that required for verification
            self.veri_queue.pop(0)
            self.lock = 0
            self.bot_info = {}
            Thread(target=self.bot_detect, args=()).start()

        if len(response.users) == 1:
            if response.users[0].jid not in self.owner:
                self.bot_info['user_name'] = response.users[0].jid
                self.bot_info['screen_name'] = response.users[0].display_name

                if len(self.bot_info) == 5:
                    try:
                        self.verify.bot(self.bot_info)
                    finally:
                        self.bot_info = {}
                        self.veri_queue.pop(0)
                        self.lock = 0
                        Thread(target=self.bot_detect, args=()).start()

        self.databaseUpdate.update(response.u)

    def on_group_sysmsg_received(self, response: chatting.IncomingGroupSysmsg):
        print("[+] System message in {}: {}".format(response.group_jid, response.sysmsg))

        if 'added you' in response.sysmsg:
            if Database('data.db').check_existence(response.group_jid) is False:
                self.databaseUpdate.added_first_time(response.group_jid, response.group.owner, response.group.admins)
            else:
                Database('data.db').update_join_time(response.group_jid, time.time())
        elif 'removed from the group' in response.sysmsg:
            self.databaseUpdate.delete_group_info(response.group_jid)

    def on_group_status_received(self, response: chatting.IncomingGroupStatus):
        print("[+] Status message in {}: {}".format(response.group_jid, response.status))

        if 'invited' not in response.status and 'has joined the chat' in response.status:
            self.veri_queue.append([response.group_jid, response.status_jid])
            print(colorama.Fore.RED + str(self.veri_queue))
            Thread(target=self.bot_detect, args=()).start()

        if 'has joined the chat' in response.status:
            if len(response.group.admins) == 1:
                self.owner.append(
                    response.group.owner[0])  # to differentiate between database update and bot verify in peer response

            print("######self.owner########", self.owner)
            if Database('data.db').check_existence(response.group_jid) is True:
                self.databaseUpdate.admin_update(response.group_jid, response.group.owner, response.group.admins)
            else:
                self.databaseUpdate.added_first_time(response.group_jid, response.group.owner, response.group.admins)

        if 'invited' in response.status:
            welcome_msg = Database('data.db').get_welcome_msg(response.group_jid)
            if welcome_msg is not None:
                self.client.send_chat_message(response.group_jid, welcome_msg)
        # self.t = time.time()

    def on_status_message_received(self, response: chatting.IncomingStatusResponse):
        print("[+] Status message from {}: {}".format(response.from_jid, response.status))

    def on_username_uniqueness_received(self, response: UsernameUniquenessResponse):
        print("Is {} a unique username? {}".format(response.username, response.unique))

    def on_sign_up_ended(self, response: RegisterResponse):
        print("[+] Registered as " + response.kik_node)

    # Error handling

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("[-] Connection failed: " + response.message)

    def on_login_error(self, login_error: LoginError):
        if login_error.is_captcha():
            login_error.solve_captcha_wizard(self.client)

    def on_register_error(self, response: SignUpError):
        print("[-] Register error: {}".format(response.message))


if __name__ == '__main__':
    main()
