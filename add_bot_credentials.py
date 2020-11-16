import sys
import random
import binascii
import main.bot_config as botconfig


def random_bytes(n):
    a = bytes([random.randint(0, 255) for _ in range(n)])
    b = binascii.hexlify(a)
    return b.decode("ascii")


def random_device():
    device_one = ["311870", "lg", "LG G8 ThinQ", "29", "1570976775000", "6", "3"]
    device_two = ["310004", "google", "Google Pixel 4 XL", "29", "1584266226000", "2", "2"]
    device_three = ["310016", "samsung", "Samsung Galaxy S10e", "29", "1588497762000", "4", "1"]
    device_four = ["310160", "samsung", "Samsung Galaxy S20+", "29", "1592592670000", "1", "2"]
    device_five = ["310120", "lg", "LG V30", "28", "1594696948000", "3", "1"]
    device_list = [device_one, device_two, device_three, device_four, device_five]
    device = random.choice(device_list)
    return device


# if len(sys.argv) != 4:
#     print("Usage: " + sys.argv[0] + " username (kik username) password (kik password) name (adam/eve) bot_id (1)")
#     exit(-1)


def add_bot(username, password, name, bot_id):
    device_config = random_device()
    bot_configuration = botconfig.BotConfiguration()

    bot_configuration.username = username
    bot_configuration.password = password
    bot_configuration.name = "Eve Assistant" if name == "" else name
    bot_configuration.bot_id = bot_id
    bot_configuration.android_id = random_bytes(8)
    bot_configuration.device_id = random_bytes(16)
    bot_configuration.operator = device_config[0]
    bot_configuration.brand = device_config[1]
    bot_configuration.model = device_config[2]
    bot_configuration.android_sdk = device_config[3]
    bot_configuration.install_date = device_config[4]
    bot_configuration.logins_since_install = device_config[5]
    bot_configuration.registrations_since_install = device_config[6]
    print(device_config)
    botconfig.add_bot(bot_configuration)

    print("Added user #" + username + "\n Name: " + name + "\n Bot ID: " + bot_id)


if __name__ == '__main__':
    username = input("enter username: ")
    password = input("enter password: ")
    name = input("enter name: ")
    bot_id = input("enter bot id: ")
    add_bot(username, password, name, bot_id)
