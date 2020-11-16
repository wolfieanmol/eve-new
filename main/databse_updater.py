from main.database import Database
import time


class DatabaseUpdate:
    def __init__(self, client):
        self.client = client
        self.buffer = []

    def update(self, users):
        # a = [ast.literal_eval(e) for e in users]
        admins = {k: v for k, v in users}
        print(set(admins.keys()))
        print(self.buffer)
        for buffer in self.buffer:
            if set(buffer[3]) == set(admins.keys()):
                if buffer[0] == 'admin_update':
                    print(buffer)
                    Database("data.db").update_admins(buffer[1], str(buffer[2]),
                                                      str(admins))
                    self.check_own_owner(users, buffer)

                elif buffer[0] == 'group_init':
                    Database("data.db").group_init(buffer[1], time.time(), "on", "on", str(buffer[2]),
                                                   str(admins), 180, None, 20)
                self.buffer.remove(buffer)

    def check_own_owner(self, users, buffer):
        """ leaving if only rage and/or eve are admin """

        if len(users) == 1:
            for ad in users:
                if ad[1].lower() == "eve (assistant)":
                    self.delete_group_info(buffer[1])
                    self.client.leave_group(buffer[1])

        if len(users) == 2:
            c = 0
            for ad in users:
                if ad[1].lower() == "eve (assistant)" or ad[1].lower() == "rage bot":
                    c += 1
            if c == 2:
                self.delete_group_info(buffer[1])
                self.client.leave_group(buffer[1])

    def added_first_time(self, group_jid, owner, admins_jid):
        self.buffer.append(('group_init', group_jid, owner, admins_jid))
        self.client.request_info_of_jids(admins_jid)

    def admin_update(self, group_jid, owner, admins_jid):
        self.buffer.append(('admin_update', group_jid, owner, admins_jid))
        self.client.request_info_of_jids(admins_jid)

    def delete_group_info(self, group_jid):
        Database('data.db').delete_row(group_jid)

    def welcome_message(self, welcome_msg, group_jid, peer_jid):
        message = Database('data.db').update_welcome_msg(welcome_msg, group_jid, peer_jid)
        self.client.send_chat_message(group_jid,
                                      "welcome message set to:\n {}".format(welcome_msg) if message is 1
                                      else "Nice try Rage" if message is 2
                                      else "welcome message can only be set by an admin")
