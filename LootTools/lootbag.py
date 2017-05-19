from BotGlobals import RARITIES
from collections import defaultdict

class LootBag(object):
    loot_rarities = [r for r in RARITIES]
    def __init__(self):

        self._rarities = LootBag.loot_rarities
        #Loot slots will be dictionaries to the counts of loot.
        #Defaults to 0
        self.loot_slots = {r: {} for r in self._rarities}

    def add_loot(self, rarity, loot_name):
        try:
            self.loot_slots[rarity][loot_name] += 1
        except KeyError:
            self.loot_slots[rarity] = {loot_name: 1}

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
        to_del = []
        for r in self.loot_slots.keys():
            for l in self.loot_slots[r].keys():
                if self.loot_slots[r][l] < 1:
                    to_del += [(r, l)]

        for k, l in to_del:
            try:
                del (self.loot_slots[r][l])
            except KeyError:
                pass

    def get_loot_dict(self):
        return self.loot_slots
