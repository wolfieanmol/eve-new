from main.database import Database
import os
import shelve


class Migration:
    def __init__(self):
        self.database = Database("data.db")

    def file_read(self):
        self.database.create_table("group_info(group_jid TEXT NOT NULL, join_time REAL, wiki_status TEXT, "
                                   "verification_status TEXT, owner TEXT, admins TEXT, PRIMARY KEY(group_jid))")
        directory = os.fsencode("/home/wolfie/kik-bot-api-unofficial/examples")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".dat") and filename.startswith("11"):
                self.database.migrate_data(filename.split('_')[0] + "_" + filename.split('_')[1], None, "on", "on",
                                           None, None)
        self.database.cursor.close()
        self.database.connection.close()
        # if os.path.isfile(filename.split('.')[0]) or os.path.isfile(filename.split('.')[0] + '.dir'):
        #     with shelve.open(filename, writeback=True) as f:
        #         if variable_name in f.keys():
        #             print('1')
        #             return f[variable_name]
        #         else:
        #             return None

    def name_migration(self):
        self.database.create_table()

        directory = os.fsencode("/home/wolfie/Downloads/15jun/home/anmol/kik-bot-api-unofficial/examples")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith("_data") and filename.startswith("11"):
                print(filename)
                # if os.path.isfile(filename.split('.')[0]) or os.path.isfile(filename.split('.')[0] + '.dir'):
                with shelve.open("/home/wolfie/Downloads/15jun/home/anmol/kik-bot-api-unofficial/examples/" + filename) as f:
                    print((list(f.keys())))
                    if "name_dict" in f.keys():
                        print('1')
                        names = f["name_dict"]
                    else:
                        names = {}


                print(names)
                # self.database.name_migration(filename.split('_')[0] + "_" + filename.split('_')[1], names)

        self.database.cursor.close()
        self.database.connection.close()

    def drop_table(self):
        self.database.drop_table()

obj = Migration()
obj.drop_table()
