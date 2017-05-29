from collections import defaultdict
from os.path import isfile, join
from .lootbag import LootBag
from BotGlobals import RARITIES, RARITY_COLORS
import pickle
import discord

class LootTracker(object):
    def __new__(cls, *args, **kwargs):
        #Load the LootTracker

        if(len(args) > 0):
            save_location = args[0]
        else:
            try:
                save_location = kwargs['save_location']
            except KeyError:
                return super(LootTracker, cls).__new__(cls)

        if(isfile(save_location)):
            with open(save_location, 'rb') as f:
                loaded_self = pickle.load(f)
            assert isinstance(loaded_self, LootTracker)
            print("Load success!")
            return loaded_self
        else:
            return super(LootTracker, cls).__new__(cls)

    def __init__(self, save_location = None, loot_mult = 300.0,\
                 rarities = RARITIES, rarity_colors = RARITY_COLORS,
                 rollback_rarities = ["Rollback"]):

        #Set the loot rarities to see!
        LootBag.loot_rarities = [r for r in LootBag.loot_rarities\
                     if not (r in rollback_rarities)]

        self.loot_rarities = LootBag.loot_rarities

        self.rollbacks = rollback_rarities

        not_rollback_points = [rarities[k] for k in rarities\
                        if not (k in rollback_rarities)]

        #Dict to find point values
        weight = sum(not_rollback_points)*loot_mult/len(not_rollback_points)

        self.rarities_to_points = {k: int(weight/rarities[k])\
                                   for k in rarities\
                                   if not (k in rollback_rarities)}



        if(isfile(save_location)):
            ## Means we loaded the LootTracker already!
            return

        else:
            #Point Tracker for players
            self.players_to_points = defaultdict(int)

            #Place to store data
            self.save_location = save_location

            #Player Loot tracker
            self.players_to_loot = defaultdict(LootBag)

    def add_loot(self, player, rarity, loot_name):
        if rarity in self.rollbacks:
            self.rollback(player)
        else:
            self.players_to_points[player] += self.rarities_to_points[rarity]
            self.players_to_loot[player].add_loot(rarity, loot_name)
        self.save()

    __call__ = add_loot #alias

    def get_lootBag(self, player):
        return self.players_to_loot[player]

    def get_points(self, player):
        return self.players_to_points[player]

    def get_loot_embed(self, player, bot, bot_name = 'Back Bot'):
        lootBag = self.get_lootBag(player)

        em = discord.Embed(title=":back: Loot for "+ player +": " +\
                           str(self.get_points(player)),\
                           color = discord.Color.gold())
        key_list = [r for r in self.rarities_to_points.keys()]
        key_list.sort(key=self.rarities_to_points.__getitem__)
        for r in key_list:
            field = self._rarity_field(r, lootBag.get_loot_dict()[r])
            em.add_field(**field, inline=True)
        em.add_field(**self._rollback_warn_field(), inline = False)
        em.set_author(name=bot_name, icon_url=bot.user.avatar_url)
        return em

    def _rarity_field(self, rarity, loot):
        total = sum(count for count in loot.values())
        value = '\n'.join([item + ": " + str(loot[item]) for item in loot])
        if value == '':
            value = 'None Yet!'

        return {"name": rarity + ": " + str(total) + " (" + str(self.rarities_to_points[rarity]) +\
                                   " points back)",\
                "value": value}

    def _rollback_warn_field(self):
        return {"name": "BEWARE OF THE ROLLBACK!",\
                "value": "IT WILL TAKE BACK YOUR LOOT!"}


    def get_leaderboad_embed(self, rarity_file_totals, bot, bot_name = 'Back Bot'):
        player_to_rank = self._gen_player_to_rank_dict()
        players_sorted_by_rank = sorted(player_to_rank, key = lambda p: player_to_rank[p])
        em = discord.Embed(title=":back: BOARD: ", color = discord.Color.dark_gold())
        for p in players_sorted_by_rank:
            if(player_to_rank[p] == max(player_to_rank.values())):
                rank_str = "Coming in :back:"
            else:
                rank_str = "#" + str(player_to_rank[p])
            field = self._player_rank_field(p, rank_str, rarity_file_totals)
            em.add_field(**field, inline=False)
        em.set_author(name=bot_name, icon_url=bot.user.avatar_url)
        return em

    def _gen_player_to_rank_dict(self):
        points_sorted = sorted([i for i in set(self.players_to_points.values())],\
                               reverse = True)
        return {p: points_sorted.index(self.players_to_points[p]) + 1\
                for p in self.players_to_points.keys()}

    def _player_rank_field(self, player, rank_str, rarity_file_totals):
        loot_dict_for_player = self.get_lootBag(player).get_loot_dict()
        loot_counts_for_player = {r: len(loot_dict_for_player[r]) for r in self.loot_rarities}
        return {"name": rank_str + " " + player + ": " + str(self.players_to_points[player]),
                "value": "\n".join(r + ": " + str(loot_counts_for_player[r]) + " / " +\
                                   str(rarity_file_totals[r]) for r in self.loot_rarities)}

    def save(self):
        if self.save_location != None:
            with open(self.save_location, 'wb') as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def clean(self):
        for l in self.players_to_loot.values():
            l.clean()

    def rollback(self, player):
        try:
            del self.players_to_points[player]
            del self.players_to_loot[player]
        except KeyError:
            pass

    def playback(self, player, loot_name, base_back_dir):
        rarity = self.players_to_loot[player].rm_loot(loot_name)
        if(rarity):
            self.save()
            return join(base_back_dir, rarity, loot_name)
        return
