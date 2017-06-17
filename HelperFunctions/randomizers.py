from BotGlobals import  BACK_FILE_DICT, RARITIES,\
                        CRATE_PITTY_WEIGHT, REBACK_THRESHOLD_DEFAULT
import random
from collections import defaultdict

def pick_random_file(file_dict = BACK_FILE_DICT, rarities = RARITIES):
    """
    Picks a random back file
    Input:
        file_dict: dictionary for back files
        rarities: rarities to roll for and their weights in a dictionary

    Output:
        A file from file_dict
    """
    total = sum(f for f in rarities.values())
    roll = random.randint(1, total)
    acc = 0
    for r in rarities:
        acc+=rarities[r]
        if roll <= acc:
            return pick_random_from_list(file_dict[r])

def pick_random_from_list(in_list):
    return in_list[random.randint(0, len(inList) - 1)]

def roll_for_crate(miss_streak = 0, pitty_weight = CRATE_PITTY_WEIGHT):
    return random.randint(0, pitty_weight) <= miss_streak

def unbox_crate(keys_used, key_multiplier = 1,\
                reback_threshold = REBACK_THRESHOLD_DEFAULT\
                file_dict = BACK_FILE_DICT, rarities = RARITIES):
    """
    Unboxes a crate
    Input:
        keys_used: Number of keys used to open the crate
        key_multiplier: Multiplier on keys
        reback_threshold: Threshold on multiple rolls of the same back
                          to obtain a "reback" instead of a normal back.
        file_dict: dictionary for back files
        rarities: rarities to roll for and their weights in a dictionary

    Output:
        {'rebacks' -> set(back_files), 'normal' -> set(back_files)}
    """
    accumulated_backs = defaultdict(int)
    for i in range(int(keys_used * multiplier)):
        accumulated_backs[pick_random_file(file_dict, rarities)] += 1

    backs_to_give = defaultdict(set)

    for back, count in accumulatedBacks.items():
        if count >= reback_threshold:
            backs_to_give['reback'].add(back)
        else:
            backs_to_give['normal'].add(back)

    return backs_to_give
