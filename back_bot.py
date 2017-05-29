import discord
import logging
from os import environ
from BotGlobals import BACK_BOT
import Events.botEvents
from LootTools import LootTracker, LootBag
from sys import argv



if __name__ == "__main__":
    ##TODO: Debug mode
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    print("discord.py v{v}".format(v=discord.__version__))
    if("--clean" in argv):
        lt = LootTracker("loot.pickle")
        lt.clean()
        lt.save()
    else:
        if not discord.opus.is_loaded():
            # the 'opus' library here is opus.dll on windows
            # or libopus.so on linux in the current directory
            # you should replace this with the location the
            # opus library is located in and with the proper filename.
            # note that on windows this DLL is automatically provided for you
            discord.opus.load_opus('/usr/lib/libopus.so.0')

        ##Python dependency injector: Not hard!
        BACK_BOT.lootTracker = LootTracker("loot.pickle")
        if "TOKEN" in environ:
            key = environ.get("TOKEN")
        else:
            with open("super_secret_key.txt") as f:
                key = f.readlines()[0].rstrip()
        BACK_BOT.run(key)
