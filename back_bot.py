import discord
from discord.ext.commands import Bot
import discord.opus as opus
import time
import random
import asyncio
from collections import defaultdict
from os import listdir
from os.path import relpath, isfile, join

##GLOBALS

BACK_FILE_DIR = relpath("back_files")

#Dictionary of rarities with their relative, integer weights.
#Rarest is 1.
RARITIES = {"Rare": 1,
            "Uncommon": 9,
            "Common": 40}

RARITY_COLORS = { "Rare": discord.Color.purple(),
                  "Uncommon": discord.Color.blue(),
                  "Common": discord.Color.green()}

RARITY_COLORS.setdefault(discord.Color.default())

BACK_FILE_DICT = {r: [join(BACK_FILE_DIR, r, f) for f in \
                      listdir(join(BACK_FILE_DIR, r)) if\
                      isfile(join(BACK_FILE_DIR, r, f))]\
                            for r in RARITIES}

BACK_BOT = Bot("~")

##CLASSES AND CLASS HELPERS
def LootBag_factory(rarities):
    class LootBag(object):
        def __init__(self):
            
            #Loot slots will be dictionaries to the counts of loot.
            #Defaults to 0
            self.loot_slots = {r: defaultdict(int) for r in rarities}
            
        def add_loot(self, rarity, loot_name):
            try:
                self.loot_slots[rarity][loot_name] += 1
            except KeyError:
                self.loot_slots[rarity] = defaultdict(int)
                self.loot_slots[rarity][loot_name] += 1
            
        def get_loot_dict(self):
            return self.loot_slots
        
    return LootBag
        
class LootTracker(object):
    def __init__(self, saveLocation = None, loot_mult = 100.0,\
                 rarities = RARITIES, rarity_colors = RARITY_COLORS):
        
        #Place to store data
        self.saveLocation = saveLocation 
        
        #Dict to find point values
        numerator = sum(RARITIES.values())*loot_mult
        self.rarities_to_points = {k: int(numerator/rarities[k])\
                                   for k in rarities}
        
        #Point Tracker for players
        self.players_to_points = defaultdict(int)
        
        #Make the LootBag class
        LootBag = LootBag_factory(rarities)
        
        #Player Loot tracker
        self.players_to_loot = defaultdict(LootBag)
        
        #Colors of rarities
        self.rarity_colors = rarity_colors
    
    def add_loot(self, player, rarity, loot_name):
        self.players_to_points[player] += self.rarities_to_points[rarity]
        self.players_to_loot[player].add_loot(rarity, loot_name)
        
    __call__ = add_loot #alias
        
    def get_lootBag(self, player):
        return self.players_to_loot[player]
        
    def get_points(self, player):
        return self.players_to_points[player]
    
    def get_loot_embed(self, player, bot = BACK_BOT, bot_name = 'Back Bot'):
        lootBag = self.get_lootBag(player)
        
        em = discord.Embed(title=":back: Loot for "+player +": " +\
                           str(self.get_points(player)),\
                           color = discord.Color.gold())
        key_list = [r for r in self.rarities_to_points.keys()]
        key_list.sort(key=self.rarities_to_points.__getitem__)
        for r in key_list:
            field = self._rarity_field(r, lootBag.get_loot_dict()[r])
            em.add_field(**field, inline=False)
            
        em.set_author(name=bot_name, icon_url=bot.user.avatar_url)
        return em
    
    def _rarity_field(self, rarity, loot):
        total = sum(count for count in loot.values())
        value = '\n'.join([item + ": " + str(loot[item]) for item in loot])
        if value == '':
            value = 'None Yet!'
            
        return {"name": rarity +": " + str(total) + "\n(" + str(self.rarities_to_points[rarity]) +\
                                   " points back)",\
                "value": value}
    
    def save(self): #TODO
        pass

##Python dependency injector: Not hard!
BACK_BOT.lootTracker = LootTracker()
    
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

async def nil_corout():
    return

async def play_opus_audio_to_channel_then_leave(message, opus_filename,\
                                           failure_coroutine = nil_corout,
                                           back_bot = BACK_BOT,
                                           rarity_colors = RARITY_COLORS):
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
#           voice_client = await BACK_BOT.join_voice_channel(message.author.voice.voice_channel)
            async def join_the_channel():
                return await asyncio.shield(back_bot.join_voice_channel(\
                                message.author.voice.voice_channel))
                
            voice_client = await join_the_channel()
                    #Play the audio, then disconnect
            try:
                
                def disconnect_from_vc(*args):
    #                print("after called")
                    dc_fut = asyncio.run_coroutine_threadsafe(voice_client.disconnect(), BACK_BOT.loop)
                    try:
                        dc_fut.result()
                    except:
                        pass
                    
                player = voice_client.create_ffmpeg_player(opus_filename, after = disconnect_from_vc)
                
                player.start()
                
                
                
    #            time.sleep(staytime_seconds)
    #            await voice_client.disconnect()
                
            except Exception as e:
                await voice_client.disconnect()
                await failure_coroutine()
                raise e
            
            
        except Exception as e:
            print("Hang back! No audio play!")
            await failure_coroutine()
            
        base, rarity, clip  = opus_filename.split("\\")
        color = rarity_colors[rarity]
        em = discord.Embed(title= rarity + " :back:",\
                           description = clip,\
                           color=color)
        em.set_author(name='Back Bot', icon_url=BACK_BOT.user.avatar_url)
        await BACK_BOT.send_message(message.channel, embed=em)
        
        BACK_BOT.lootTracker(message.author.name, rarity, clip)
            

    else:
        await failure_coroutine()
    #EXIT
    

@BACK_BOT.event
async def on_read():
    print("Back into action")


message_loop = asyncio.get_event_loop()
@BACK_BOT.event
async def on_message(message):
    if(("back" in message.content.lower()) and (message.author.id != BACK_BOT.user.id)\
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
    em = BACK_BOT.lootTracker.get_loot_embed(message.author.name)
    return await BACK_BOT.send_message(message.channel, 
                                       embed=em)

if __name__ == "__main__":
    with open("super_secret_key.txt") as f:
        key = f.readlines()[0].rstrip()
    BACK_BOT.run(key)