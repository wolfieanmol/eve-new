import mongoengine as me


class Substitutions(me.EmbeddedDocument):
    key = me.StringField()
    value = me.StringField()
    user_jid = me.StringField()
    admin = me.BooleanField(default=False)


class Group(me.Document):
    group_jid = me.StringField()
    substitutions = me.EmbeddedDocumentListField(Substitutions)

    meta = {
        'db_alias': 'groups_db',
        'collection': 'groups'
    }


class MongoDatabase:
    def __init__(self):
        me.connect(db="groups", alias="groups_db")

    def save_substitutions(self, group: Group, key, value, is_admin=False, from_jid=None):
        subs = Substitutions()
        subs.key = key
        subs.value = value
        subs.admin = is_admin
        if from_jid is not None:
            subs.user_jid = from_jid
        group.substitutions.append(subs)
        group.save()

    def find_by_jid(self, group_jid) -> Group:
        print(group_jid)
        group = Group.objects(group_jid=group_jid).first()
        return group

    def find_by_key(self, key):
        value = Substitutions.objects(key=key)