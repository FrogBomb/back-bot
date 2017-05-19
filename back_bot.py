import discord
from discord.ext.commands import Bot
import discord.opus as opus
import time
import random
import asyncio
from collections import defaultdict
from os import environ
from os import listdir
from os.path import relpath, isfile, join, split
import pickle

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
BACK_BOT = Bot(CMD_PREFIX)
ROLLBACK_THRESHOLD = 10000
##CLASSES
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
            except KeyError:
                pass
        return

    def get_loot_dict(self):
        return self.loot_slots


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

    def __init__(self, save_location = None, loot_mult = 100.0,\
                 rarities = RARITIES, rarity_colors = RARITY_COLORS,
                 rollback_rarities = ["Rollback"]):

        #Set the loot rarities to see!
        LootBag.loot_rarities = [r for r in LootBag.loot_rarities\
                     if not (r in rollback_rarities)]

        self.loot_rarities = LootBag.loot_rarities

        self.rollbacks = rollback_rarities

        #Dict to find point values
        numerator = sum(rarities[k] for k in rarities\
                        if not (k in rollback_rarities))*loot_mult

        self.rarities_to_points = {k: int(numerator/rarities[k])\
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

##FUNCTIONS
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

def back_embed(clip, rarity, rarity_colors, back_bot = BACK_BOT):
            color = rarity_colors[rarity]
            em = discord.Embed(title= rarity + " :back:",\
                               description = clip,\
                               color=color)
            em.set_author(name='Back Bot', icon_url=back_bot.user.avatar_url)
            return em

async def nil_corout():
    return

async def play_opus_audio_to_channel_then_leave(message, opus_filename,\
                                           failure_coroutine = nil_corout,
                                           back_bot = BACK_BOT,
                                           rarity_colors = RARITY_COLORS,
                                           give_loot = True):
    """
    Plays a .opus audio file through the bot.

    The bot will join the channel of the Member associated with the message if
    possible. Then, will play the audio file, and leave after staytime_seconds.

    If there is a failure for whatever reason, the failure_coroutine will run
    with no arguements. Most errors will be raised afterward.

    """

    if(opus.is_loaded() and isinstance(message.author, discord.Member)\
       and message.author.voice.voice_channel != None):
        print(opus_filename)
        #Move to the correct voice channel
        if(back_bot.is_voice_connected(message.author.server)):
            voice_client = back_bot.voice_client_in(message.author.server)
            await voice_client.disconnect()
        try:
            voice_client = await back_bot.join_voice_channel(message.author.voice.voice_channel)

            #Play the audio, then disconnect
            try:

                def disconnect_from_vc(*args):
                    dc_fut = asyncio.run_coroutine_threadsafe(voice_client.disconnect(), back_bot.loop)
                    try:
                        dc_fut.result()
                    except:
                        dc_fut.cancel()

                player = voice_client.create_ffmpeg_player(opus_filename, after = disconnect_from_vc)

                player.start()

            except Exception as e:
                await asyncio.shield(voice_client.disconnect())
                await failure_coroutine()
                raise e

        except discord.errors.ConnectionClosed as cE:
            print("There's a connection backup!", cE)
            return

        except Exception as e:
            print("Hang back! No audio play!")
            await failure_coroutine()
            raise e

        head, clip  = split(opus_filename)
        base, rarity = split(head)
        em = back_embed(clip, rarity, rarity_colors, back_bot)
        await back_bot.send_message(message.channel, embed=em)
        if(give_loot):
            back_bot.lootTracker(message.author.name, rarity, clip)

    else:
        await failure_coroutine()
    #EXIT

@BACK_BOT.event
async def on_read():
    print("Back into action")

@BACK_BOT.event
async def on_message(message):
    if(len(message.content)>0 and message.content[:len(CMD_PREFIX)] == CMD_PREFIX):
        pass
    elif((("back" in message.content.lower())\
            or ("\U0001f519" in message.content.lower()))\
       and (message.author.id != BACK_BOT.user.id)\
       and BACK_BOT.voice_client_in(message.server) == None):

        print("back found! " + message.author.name + " is back at " + time.asctime())
        async def say_back_message():
            await BACK_BOT.send_message(message.channel, "Did somebody say back?")

        filename = pick_random_file()
        await play_opus_audio_to_channel_then_leave(message, filename,\
                                               failure_coroutine = say_back_message)

    await BACK_BOT.process_commands(message)


@BACK_BOT.command()
async def im_back(*args):
    return await BACK_BOT.say("Hi Back")

@BACK_BOT.command()
async def am_i_back(*args):
    return await BACK_BOT.say("Yes Back, you are Back")

@BACK_BOT.command()
async def bitch(*args):
    return await BACK_BOT.say("I ain't no back bitch")

@BACK_BOT.command(pass_context=True)
async def loot(context):
    message = context.message
    em = BACK_BOT.lootTracker.get_loot_embed(message.author.name, BACK_BOT)
    return await BACK_BOT.send_message(message.channel,
                                       embed=em)
@BACK_BOT.command(pass_context=True)
async def board(context):
    message = context.message
    rarity_file_totals = {r: len(BACK_FILE_DICT[r]) for r in RARITIES}
    em = BACK_BOT.lootTracker.get_leaderboad_embed(rarity_file_totals, BACK_BOT)
    return await BACK_BOT.send_message(message.channel,
                                       embed=em)

@BACK_BOT.command(pass_context=True)
async def playback(context):
    message = context.message
    back_to_play = (message.content).split(" ")[1]
    filename = BACK_BOT.lootTracker.playback(message.author.name, back_to_play, BACK_FILE_DIR)
    if(filename):
        return await play_opus_audio_to_channel_then_leave(message, filename, give_loot=False)

@BACK_BOT.command(pass_context=True)
async def rollback(context):
    message = context.message
    if BACK_BOT.lootTracker.get_points(message.author.name) >= ROLLBACK_THRESHOLD:
        filename = pick_random_file(rarities = {"Rollback": 1})
        return await play_opus_audio_to_channel_then_leave(message, filename)
    else:
        return await BACK_BOT.say("You have to have over " +\
                                  str(ROLLBACK_THRESHOLD) +\
                                  " Points to force a Rollback!")

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

    if "TOKEN" in environ:
        key = environ.get("TOKEN")
    else:
        with open("super_secret_key.txt") as f:
            key = f.readlines()[0].rstrip()
    BACK_BOT.run(key)
