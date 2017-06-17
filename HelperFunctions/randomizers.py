from BotGlobals import BACK_FILE_DICT, RARITIES, CRATE_PITTY_WEIGHT
import random

def pick_random_file(file_dict = BACK_FILE_DICT, rarities = RARITIES):
    total = sum(f for f in rarities.values())
    roll = random.randint(1, total)
    acc = 0
    for r in rarities:
        acc+=rarities[r]
        if roll <= acc:
            return pick_random_from_list(file_dict[r])

def pick_random_from_list(inList):
    return inList[random.randint(0, len(inList) - 1)]

def roll_for_crate(miss_streak = 0, pitty_weight = CRATE_PITTY_WEIGHT):
    return random.randint(0, pitty_weight) <= miss_streak
