import discord
from os import environ
from BotGlobals import BACK_BOT
import Events.botEvents
from LootTools import LootTracker, LootBag

if __name__ == "__main__":
    if not discord.opus.is_loaded():
        # the 'opus' library here is opus.dll on windows
        # or libopus.so on linux in the current directory
        # you should replace this with the location the
        # opus library is located in and with the proper filename.
        # note that on windows this DLL is automatically provided for you
        discord.opus.load_opus('/usr/lib/libopus.so.0')

    ##Python dependency injector: Not hard!
    BACK_BOT.lootTracker = LootTracker("loot.pickle")
    BACK_BOT.lootTracker.clean()
    if "TOKEN" in environ:
        key = environ.get("TOKEN")
    else:
        with open("super_secret_key.txt") as f:
            key = f.readlines()[0].rstrip()
    BACK_BOT.run(key)
