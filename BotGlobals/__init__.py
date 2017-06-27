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

BACK_WORDS = [  "prapa",
                "Atzera",
                "таму",
                "natrag",
                "обратно",
                "esquena",
                "natrag",
                "zpět",
                "tilbage",
                "terug",
                "tagasi",
                "takaisin",
                "arrière",
                "de volta",
                "zurück",
                "πίσω",
                "vissza",
                "aftur",
                "ar ais",
                "indietro",
                "atpakaļ",
                "atgal",
                "назад",
                "lura",
                "tilbake",
                "plecy",
                "costas",
                "spate",
                "назад",
                "назад",
                "späť",
                "nazaj",
                "espalda",
                "tillbaka",
                "назад",
                "yn ôl",
                "צוריק",
                "ետ",
                "geri",
                "পিছনে",
                "背部",
                "後面",
                "უკან",
                "પાછા",
                "वापस",
                "rov qab",
                "バック",
                "ಮತ್ತೆ",
                "артқа",
                "ត្រឡប់​មក​វិញ",
                "백",
                "ກັບ​ຄືນ​ໄປ​ບ່ອນ",
                "തിരികെ",
                "परत",
                "буцах",
                "နောက်ကျော",
                "फिर्ता",
                "ආපසු",
                "бозгашт",
                "மீண்டும்",
                "తిరిగి",
                "กลับ",
                "واپس",
                "orqa",
                "trở lại",
                "إلى الوراء",
                "חזור",
                "بازگشت",
                "geri",
                "terug",
                "mmbuyo",
                "baya",
                "azụ",
                "khutlela",
                "dib",
                "nyuma",
                "pada",
                "emuva",
                "balik",
                "likod",
                "kembali",
                "bali",
                "indray",
                "kembali",
                "hoki",
                "reen",
                "tounen",
                "back",
                "\U0001f519",
                "⠃⠁⠉⠅"]
