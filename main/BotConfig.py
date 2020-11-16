import json

filename = "botconfig.json";


def read_as_json():
    with open(filename) as json_file:
        data = json.load(json_file);
    return data;


def get_bots():
    bot_configurations = [];
    data = read_as_json();
    for botname in data:
        bot_configuration = BotConfiguration();
        bot_configuration.username = botname;
        bot_configuration.password = data[botname][0]
        bot_configuration.android_id = data[botname][1];
        bot_configuration.device_id = data[botname][2];
        bot_configurations.append(bot_configuration);
    return bot_configurations;


def get_first_bot():
    return get_bots()[0];


def add(bot_configuration):
    data = read_as_json();
    data[bot_configuration.username] = [bot_configuration.password, bot_configuration.android_id,
                                        bot_configuration.device_id];
    with open(filename, "w") as json_file:
        json.dump(data, json_file);


class BotConfiguration():
    username = "";
    password = "";
    android_id = "";
    device_id = "";
