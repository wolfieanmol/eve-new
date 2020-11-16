import sqlite3 as sql
import ast


class Database:
    def __init__(self, name):
        self.connection = sql.connect(name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user_info(group_jid TEXT NOT NULL, peer_jid TEXT NOT NULL, "
                            "given_name TEXT, PRIMARY KEY(peer_jid))")

    def group_init(self, group_jid, join_time, wiki_status, verification_status, owner, admins, verification_time,
                   welcome_message, verification_days):
        query = "INSERT INTO group_info (group_jid, join_time, wiki_status, verification_status, owner, admins, " \
                "verification_time, welcome_message, verification_days) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, (group_jid.split('@')[0], join_time, wiki_status, verification_status, owner,
                                    admins, verification_time, welcome_message, verification_days))
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def shift(self):
        self.cursor.execute("SELECT group_jid FROM group_info")
        data = self.cursor.fetchall()
        self.cursor.close()
        self.connection.close()
        return data

    def check_existence(self, group_jid):
        self.cursor.execute("SELECT * FROM group_info WHERE group_jid = ?", (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        print("*******database.check_existance***********")
        print(data)
        self.cursor.close()
        self.connection.close()
        return False if data == [] else True

    def delete_row(self, group_jid):
        self.cursor.execute("DELETE FROM group_info WHERE group_jid = ?", (group_jid.split('@')[0],))
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def update_verification_status(self, status, group_jid, peer_jid):
        """checks if the verification_update request is carried out by an admin. if yes then only update the
        verification_status. """

        self.cursor.execute("SELECT admins, verification_status FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        admins = ast.literal_eval(data[0][0])
        verification_status = data[0][1]

        if peer_jid in admins.keys() and verification_status != status:
            if admins[peer_jid] != "Rage bot":
                query = "UPDATE group_info SET verification_status = ? WHERE group_jid = ?"
                self.cursor.execute(query, (status, group_jid.split('@')[0]))
                self.connection.commit()
                self.cursor.close()
                self.connection.close()
                return 1
            else:
                return 4
        if peer_jid not in admins:
            return 2
        return 3

    def update_verification_time(self, new_time, group_jid, peer_jid):
        self.cursor.execute("SELECT admins FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        admins = ast.literal_eval(data[0][0])

        if peer_jid in admins.keys():
            if admins[peer_jid] != "Rage bot":
                query = "UPDATE group_info SET verification_time = ? WHERE group_jid = ?"
                self.cursor.execute(query, (new_time, group_jid.split('@')[0]))
                self.connection.commit()
                self.cursor.close()
                self.connection.close()
                return 1
            return 2
        return 3

    def update_verification_days(self, new_days, group_jid, peer_jid):
        self.cursor.execute("SELECT admins FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        admins = ast.literal_eval(data[0][0])

        if peer_jid in admins.keys():
            if admins[peer_jid] != "Rage bot":
                query = "UPDATE group_info SET verification_days = ? WHERE group_jid = ?"
                self.cursor.execute(query, (new_days, group_jid.split('@')[0]))
                self.connection.commit()
                self.cursor.close()
                self.connection.close()
                return 1
            return 2
        return 3

    def update_welcome_msg(self, welcome_msg, group_jid, peer_jid):
        self.cursor.execute("SELECT admins FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        admins = ast.literal_eval(data[0][0])

        if peer_jid in admins.keys():
            if admins[peer_jid] != "Rage bot":
                query = "UPDATE group_info SET welcome_message= ? WHERE group_jid = ?"
                self.cursor.execute(query, (welcome_msg, group_jid.split('@')[0]))
                self.connection.commit()
                self.cursor.close()
                self.connection.close()
                return 1
            return 2
        return 3

    def update_wiki_status(self, status, group_jid, peer_jid):

        self.cursor.execute("SELECT admins, wiki_status FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        admins = ast.literal_eval(data[0][0])
        verification_status = data[0][1]

        if status == ('temp' or verification_status == 'temp'):
            if status != verification_status:
                query = "UPDATE group_info SET wiki_status = ? WHERE group_jid = ?"
                self.cursor.execute(query, (status, group_jid.split('@')[0]))
                self.connection.commit()
                self.cursor.close()
                self.connection.close()
                return 5
            return 6

        else:
            if peer_jid in admins.keys() and verification_status != status:
                if admins[peer_jid] != "Rage bot":
                    query = "UPDATE group_info SET wiki_status = ? WHERE group_jid = ?"
                    self.cursor.execute(query, (status, group_jid.split('@')[0]))
                    self.connection.commit()
                    self.cursor.close()
                    self.connection.close()
                    return 1
                else:
                    return 4
            if peer_jid not in admins:
                return 2
            return 3

    def update_admins(self, group_jid, owner, admins):
        query = "UPDATE group_info SET owner = ?, admins = ? WHERE group_jid = ?"
        self.cursor.execute(query, (owner, admins, group_jid.split('@')[0]))
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def get_admins(self, group_jid):
        self.cursor.execute("SELECT admins FROM group_info WHERE group_jid = ?", (group_jid.split('@')[0],))
        admin_list = self.cursor.fetchall()
        admins = admin_list[0][0] if admin_list != [] else None
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        return admins

    def get_join_time(self, group_jid):
        self.cursor.execute("SELECT join_time FROM group_info WHERE group_jid = ?", (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        time = data[0][0] if data != [] else None
        print("time:", time)
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        return time

    def get_verification_status(self, group_jid):
        self.cursor.execute("SELECT verification_status FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        status = data[0][0] if data != [] else None
        print("status:", status)
        self.cursor.close()
        self.connection.close()
        return status

    def get_verification_time(self, group_jid):
        self.cursor.execute("SELECT verification_time FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        verification_time = data[0][0] if data != [] else None
        self.cursor.close()
        self.connection.close()
        return verification_time

    def get_verification_days(self, group_jid):
        self.cursor.execute("SELECT verification_days FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        verification_time = data[0][0] if data != [] else None
        self.cursor.close()
        self.connection.close()
        return verification_time

    def get_wiki_status(self, group_jid):
        self.cursor.execute("SELECT wiki_status FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        status = data[0][0] if data != [] else None
        print("status:", status)
        self.cursor.close()
        self.connection.close()
        return status

    def get_welcome_msg(self, group_jid):
        self.cursor.execute("SELECT welcome_message FROM group_info WHERE group_jid = ?",
                            (group_jid.split('@')[0],))
        data = self.cursor.fetchall()
        welcome_msg = data[0][0] if data != [] else None
        # print("status:", status)
        self.cursor.close()
        self.connection.close()
        return welcome_msg

    def get_all_groups(self):
        self.cursor.execute("SELECT group_jid FROM group_info")
        data = self.cursor.fetchall()
        jid = [da[0] for da in data]
        # print("status:", status)
        self.cursor.close()
        self.connection.close()
        return jid

    # --------------------------
    #  data migration
    # -------------------------

    def migrate_data(self, group_jid, join_time, wiki_status, verification_status, owner, admins):
        query = "INSERT INTO group_info (group_jid, join_time, wiki_status, verification_status, owner, admins) " \
                "VALUES (?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, (group_jid, join_time, wiki_status, verification_status, owner, admins))
        self.connection.commit()

    def name_migration(self, group_jid, names):
        for k, v in names:
            query = "INSERT INTO user_info(group_jid, peer_jid, given_name) VALUES (?, ?, ?)"
            self.cursor.execute(query, (group_jid, k, v))
            self.connection.commit()

    def drop_table(self):
        self.cursor.execute("DROP TABLE user_info")
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    # --------------------------
    #  user_info
    # -------------------------

    def given_name(self, name, group_jid, peer_jid):
        self.cursor.execute("SELECT given_name FROM user_info WHERE group_jid = ? AND peer_jid = ?",
                            (group_jid.split('@')[0], peer_jid))
        data = self.cursor.fetchall()
        print(data)
        g_name = data[0][0] if data != [] else ''
        if g_name == '':
            self.cursor.execute("INSERT INTO user_info(group_jid, peer_jid, given_name) VALUES (?, ?, ?)",
                                (group_jid.split('@')[0], peer_jid, name))
        else:
            self.cursor.execute("UPDATE user_info SET given_name = ? WHERE group_jid = ? AND peer_jid = ?",
                                (name, group_jid.split('@')[0], peer_jid))
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def get_given_name(self, group_jid, peer_jid):
        self.cursor.execute("SELECT given_name FROM user_info WHERE group_jid = ? AND peer_jid = ?",
                            (group_jid.split('@')[0], peer_jid))
        data = self.cursor.fetchall()
        print(data)
        name = data[0][0] if data != [] else ''
        self.cursor.close()
        self.connection.close()
        return name

    def delete_given_name(self, group_jid, peer_jid):
        self.cursor.execute("DELETE FROM user_info WHERE group_jid = ? AND  peer_jid = ?",
                            (group_jid.split('@')[0], peer_jid))

        self.cursor.close()
        self.connection.close()

    # --------------------------
    #  bot_info
    # -------------------------

    def bot_init(self, e):
        query = "INSERT INTO bot_info(group_jid, peer_jid, days, user_name, screen_name, pfp, removed_eve, " \
                "msg_sent, first_msg, no_of_msg) VALUES (?,?,?,?,?,?,?,?,?,?)"
        self.cursor.execute(query, (e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9]))
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
