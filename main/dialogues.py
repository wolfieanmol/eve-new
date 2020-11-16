from main import mongo


class Dialogues:
    def __init__(self, client):
        self.mongo = mongo.MongoDatabase()
        self.client = client

    def save_dialogue(self, sub, group, group_jid):
        if group is None:
            group = mongo.Group(group_jid=group_jid)
            self.mongo.save_substitutions(group, sub[0], sub[1])
            self.client.send_chat_message(group_jid, "done")
        else:
            substitution = group.substitutions.filter(key=sub[0], user_jid=None)
            if len(substitution) != 0:
                if substitution[0].admin:
                    self.client.send_chat_message(group_jid, "Admin dialogue already exists")
                else:
                    substitution.update(value=sub[1], user_jid=None)
                    group.save()
                    self.client.send_chat_message(group_jid, "done")
            else:
                self.mongo.save_substitutions(group, sub[0], sub[1])
                self.client.send_chat_message(group_jid, "done")

    def save_admin_dialogue(self, sub, group, group_jid):
        if group is None:
            group = mongo.Group(group_jid=group_jid)
            self.mongo.save_substitutions(group, sub[0], sub[1], is_admin=True)
            self.client.send_chat_message(group_jid, "done")
        else:
            substitution = group.substitutions.filter(key=sub[0])
            if len(substitution) != 0:
                print(substitution)
                substitution.delete()
                self.mongo.save_substitutions(group, sub[0], sub[1], is_admin=True)
                substitution.update(value=sub[1], admin=True, user_jid=None)
                group.save()
                self.client.send_chat_message(group_jid, "done")
            else:
                self.mongo.save_substitutions(group, sub[0], sub[1], is_admin=True)
                self.client.send_chat_message(group_jid, "done")

    def save_user_dialogue(self, sub, group, group_jid, from_jid=None):
        if group is None:
            group = mongo.Group(group_jid=group_jid)
            self.mongo.save_substitutions(group, sub[0], sub[1], from_jid=from_jid)
            self.client.send_chat_message(group_jid, "done")
        else:
            substitution = group.substitutions.filter(key=sub[0], admin=True)
            if len(substitution) != 0:
                self.client.send_chat_message(group_jid, "Admin dialogue already exists")
            else:
                substitution = group.substitutions.filter(key=sub[0], user_jid=from_jid)
                if len(substitution) != 0:
                    substitution.update(value=sub[1])
                    group.save()
                    self.client.send_chat_message(group_jid, "done")
                else:
                    self.mongo.save_substitutions(group, sub[0], sub[1], from_jid=from_jid)
                    self.client.send_chat_message(group_jid, "done")