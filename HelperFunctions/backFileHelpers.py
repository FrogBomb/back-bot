from BotGlobals import BACK_FILE_DIR, BACK_FILE_DICT
from os.path import join

def is_a_back_file_with_rarity(rarity, back_file_name):
    try:
        return join(BACK_FILE_DIR, rarity, back_file_name) in BACK_FILE_DICT[rarity]
    except KeyError:
        return False

def get_back_file_rarity(back_file_name):
    for r in BACK_FILE_DIR.keys():
        if(is_a_back_file_with_rarity(r, back_file_name)):
            return r
