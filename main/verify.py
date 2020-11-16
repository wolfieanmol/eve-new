import pickle
from main.captcha_generator import Captcha
from threading import Thread, Timer
import time
from main.database import Database


class VerifyStatus:
    def __init__(self, client):
        self.client = client

    def set_verification_status(self, status, group_jid, peer_jid):
        message = Database("data.db").update_verification_status(status, group_jid, peer_jid)
        if status == 'off':
            self.client.send_chat_message(group_jid,
                                          "Verification turned off" if message is 1
                                          else "Verification can only be turned off by an admin" if message is 2
                                          else "Verification is already off" if message is 3 else "Nice try Rage")
        else:
            self.client.send_chat_message(group_jid,
                                          "Verification turned on" if message is 1
                                          else "Verification can only be turned on by an admin" if message is 2
                                          else "Verification is already on" if message is 3 else "Nice try Rage")

    def set_verification_time(self, new_time, group_jid, peer_jid):
        message = Database("data.db").update_verification_time(new_time, group_jid, peer_jid)
        self.client.send_chat_message(group_jid,
                                      "Verification time set to {} minutes".format(new_time // 60) if message is 1
                                      else "Nice try Rage" if message is 2
                                      else "Verification time can only be set by an admin")

    def set_verification_days(self, new_days, group_jid, peer_jid):
        message = Database("data.db").update_verification_days(new_days, group_jid, peer_jid)
        self.client.send_chat_message(group_jid,
                                      "Verification days set to {}".format(new_days) if message is 1
                                      else "Nice try Rage" if message is 2
                                      else "Verification days can only be set by an admin")


class Verify:
    def __init__(self, client):
        self.bot_peer = None
        self.client = client
        self.cap = Captcha()
        self.peer_eval = []
        self.bot_auto = {}
        self.verified = {}
        self.bot_info = []
        # self.bot_peer = []
        self.message_sent = []
        self.removed_eve = []

    def bot(self, bot_info):

        self.bot_auto = bot_info

        # self.bot_info.append(bot_info)
        print("VERIFY!!!!!!!!!!!!!", self.bot_auto)
        self.auto_remove()

        # self.bot_peer.append(bot_info[1])

    def auto_remove(self):

        """ score = 40 if self.bot_auto['days'] < 0.01 else score = 30 if self.bot_auto['days'] < 0.1 else score = 25
        if self.bot_auto['days'] < 0.5 else score = 20 if self.bot_auto['days'] < 1.0 else score = 15 if
        self.bot_auto['days'] < 5 else score = 10 """

        if self.bot_auto['days'] < 0.01:
            score = 40
        elif self.bot_auto['days'] < 0.1:
            score = 30
        elif self.bot_auto['days'] < 0.5:
            score = 25
        elif self.bot_auto['days'] < 1.0:
            score = 20
        elif self.bot_auto['days'] < 5.0:
            score = 15
        else:
            score = 10

        both_name = self.bot_auto['screen_name'].split(' ')
        if len(both_name) == 2:
            score += 5

        with open('data/bot_names.pickle', 'rb') as f:
            bot_names = pickle.load(f)
            first_name = bot_names['first_name']
            last_name = bot_names['last_name']

            if both_name[0] in first_name and both_name[1] in last_name:
                score += 25
            if both_name[0] in self.bot_auto['user_name']:
                score += 20
            if len([char for char in self.bot_auto['user_name'] if char.isdigit()]) > 2:
                score += 20

            if score >= 80:
                # self.client.send_chat_message(self.bot_auto['group_jid'], 'bot detected: ' + str(score))
                self.client.remove_peer_from_group(self.bot_auto['group_jid'], self.bot_auto['peer_jid'])
            else:
                # self.client.send_chat_message(self.bot_auto['group_jid'], 'not bot' + str(score))
                try:
                    if self.bot_auto['days'] <= Database('data.db').get_verification_days(self.bot_auto['group_jid']):
                        self.send_captcha(self.bot_auto['group_jid'], self.bot_auto['peer_jid'])
                    else:
                        welcome_msg = Database('data.db').get_welcome_msg(self.bot_auto['group_jid'])
                        if welcome_msg is not None:
                            self.client.send_chat_message(self.bot_auto['group_jid'], welcome_msg)
                except:
                    welcome_msg = Database('data.db').get_welcome_msg(self.bot_auto['group_jid'])
                    if welcome_msg is not None:
                        self.client.send_chat_message(self.bot_auto['group_jid'], welcome_msg)

            # Database('data.db').bot_init(self.bot_auto)
            # for e in self.bot_info:
            #     if e == self.bot_auto:
            #         self.bot_info.remove(e)
            #         break

            self.bot_auto = {}

    def send_captcha(self, group_jid, peer_jid):
        # TODO clear self.bot_info if verification is off. Also clear self.message_sent in both cases: veri on and off.
        time_ = Database("data.db").get_join_time(group_jid)
        join_time = 1 if time_ is None else time_
        seconds_since_join = time.time() - join_time

        verification_status = Database("data.db").get_verification_status(group_jid)
        verification_time = Database('data.db').get_verification_time(group_jid)

        if ( seconds_since_join > 43200 or join_time is 1) and verification_status != "off":
            self.client.send_chat_message(group_jid,
                                          "Type the characters in the image to prove that you are not a bot."
                                          "\nYOU WILL BE REMOVED IF YOU DO NOT SOLVE IT.")
            ans = self.cap.captcha()
            self.client.send_chat_image(group_jid, 'captcha1.jpg')
            self.peer_eval.append((peer_jid, group_jid, ans))
            self.verified[peer_jid] = False

            verify_thread = Timer(verification_time, self.captcha_removal_check, args=(group_jid, peer_jid, ans))
            verify_thread.start()
        else:
            if verification_status != "off":
                seconds_left = 43200 - seconds_since_join
                hours_left = seconds_left // 3600
                minutes_left = (seconds_left - hours_left * 3600) // 60
                self.client.send_chat_message(group_jid,
                                              "I am unable to send captchas for another : "
                                              "{} hours and {} minutes".format(hours_left, minutes_left))

    def captcha_removal_check(self, group_jid, peer_jid, ans):
        if not self.verified[peer_jid]:
            # self.removed_eve.append((group_jid, peer_jid, 1))
            self.client.send_chat_message(group_jid, 'Bye.\n If you are not a bot join again and solve the captcha')
            self.client.remove_peer_from_group(group_jid, peer_jid)

        del (self.verified[peer_jid])
        self.peer_eval.remove((peer_jid, group_jid, ans))

    def captcha_response_eval(self, peer_jid, group_jid, ans, response):
        if str(ans) in response.lower().replace(' ', ''):
            welcome_msg = Database('data.db').get_welcome_msg(group_jid)
            self.client.send_chat_message(group_jid, 'Welcome!')

            if welcome_msg is not None:
                self.client.send_chat_message(group_jid, welcome_msg)

            self.verified[peer_jid] = True
        elif not self.verified[peer_jid]:
            self.client.send_chat_message(group_jid, 'Wrong, try again')

    def eval_message(self, peer_jid, group_jid, body):
        for peer in self.peer_eval:
            if peer[0] == peer_jid and peer[1] == group_jid:
                captcha_thread = Thread(target=self.captcha_response_eval,
                                        args=(peer[0], peer[1], peer[2], body))
                captcha_thread.daemon = True
                captcha_thread.start()
                # for e in self.bot_info:
                #     if e[0] == group_jid and e[1] == peer_jid:
                #         self.message_sent.append((group_jid, peer_jid, body))
