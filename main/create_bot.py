import sys
import random
import binascii
import main.BotConfig as BotConfig

def random_bytes(n):
	a=bytes([random.randint(0,255) for _ in range(n)]);
	b=binascii.hexlify(a);
	return b.decode("ascii");

if len(sys.argv) != 3:
	print("Usage: "+sys.argv[0]+" username password");
	exit(-1);

bot_configuration=BotConfig.BotConfiguration();
bot_configuration.username=sys.argv[1];
bot_configuration.password=sys.argv[2];
bot_configuration.android_id=random_bytes(8);
bot_configuration.device_id=random_bytes(16);

BotConfig.add(bot_configuration);

print("Added user "+sys.argv[1]);

