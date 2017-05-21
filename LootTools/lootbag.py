from BotGlobals import RARITIES
from collections import defaultdict
from HelperFunctions.backFileHelpers import get_back_file_rarity, is_a_back_file_with_rarity

class LootBag(object):
    loot_rarities = [r for r in RARITIES]
    def __init__(self):

        self._rarities = LootBag.loot_rarities
        #Loot slots will be dictionaries to the counts of loot.
        #Defaults to 0
        self.loot_slots = {r: defaultdict(int) for r in self._rarities}

    def add_loot(self, rarity, loot_name):
        try:
            if(loot_name in self.loot_slots[rarity]): #If/Else for some pickles
                self.loot_slots[rarity][loot_name] += 1
            else:
                self.loot_slots[rarity][loot_name] = 1
        except KeyError:
            self.loot_slots[rarity] = defaultdict(int)
            self.loot_slots[rarity][loot_name] = 1

    def rm_loot(self, loot_name): #Returns stored rarity. None otherwise
        for r in self.loot_slots.keys():
            try:
                if self.loot_slots[r][loot_name] > 1:
                    self.loot_slots[r][loot_name] -= 1
                    return r
                elif self.loot_slots[r][loot_name] == 1:
                    del (self.loot_slots[r][loot_name])
                    return r
                else:
                    del (self.loot_slots[r][loot_name])
            except KeyError:
                pass
        return

    def clean(self):
        to_move_map = {(prevRarity, l): get_back_file_rarity(l)\
                       for prevRarity in self.loot_slots.keys()\
                       for l in self.loot_slots[prevRarity].keys()\
                       if (not is_a_back_file_with_rarity(prevRarity, l))}

        to_del = [(r, l) for r in self.loot_slots.keys()\
                  for l in self.loot_slots[r].keys()\
                  if (self.loot_slots[r][l] < 1) or\
                  ((r, l) in to_move_map and (None == to_move_map[(r, l)]))]

        for r, l in to_del:
            print("Deleting", r, l, "with the value", self.loot_slots[r][l])
            del to_move_map[(r, l)]
            del (self.loot_slots[r][l])

        for r, l in to_move_map.keys():
            print("Moving", r, l, "with the value", self.loot_slots[r][l], "to", to_move_map[(r, l)])
            new_r = to_move_map[(r, l)]
            if new_r in self.loot_slots:
                if l in self.loot_slots[new_r]:
                    # Add loot to the new location
                    self.loot_slots[new_r][l] += self.loot_slots[r][l]
                else:
                    # Move loot to the new location
                    self.loot_slots[new_r][l] = self.loot_slots[r][l]
            else:
                # Looking both ways down a one way street... pickle is scary
                self.loot_slots[new_r] = {l: self.loot_slots[r][l]}
            del self.loot_slots[r][l]

    def get_loot_dict(self):
        return self.loot_slots
