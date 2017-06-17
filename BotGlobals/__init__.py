import discord
from discord.ext.commands import Bot
from os import listdir
from os.path import relpath, join, isfile

##GLOBALS
BACK_FILE_DIR = relpath("back_files")

#Dictionary of rarities with their relative, integer weights.
#Rarest is 1.
RARITIES = {"Rollback": 1,
            "Rare": 10,
            "Uncommon": 90,
            "Common": 400}

RARITY_COLORS = { "Rollback": discord.Color(0x000000), #black
                  "Rare": discord.Color.purple(),
                  "Uncommon": discord.Color.blue(),
                  "Common": discord.Color.green()}

RARITY_COLORS.setdefault(discord.Color.default())

BACK_FILE_DICT = {r: [join(BACK_FILE_DIR, r, f) for f in \
                      listdir(join(BACK_FILE_DIR, r)) if\
                      isfile(join(BACK_FILE_DIR, r, f))]\
                            for r in RARITIES}

CMD_PREFIX = '~'
BACK_BOT = Bot(CMD_PREFIX,\
               description = "The Back Bot: A bot for the greatest joke ever told.\nJust say back...")
ROLLBACK_THRESHOLD = 10000
CRATE_PITTY_WEIGHT = 40
REBACK_THRESHOLD_DEFAULT = 3
