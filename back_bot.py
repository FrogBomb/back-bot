import discord
from discord.ext.commands import Bot
import discord.opus as opus
import time
import random
import asyncio
from os import listdir
from os.path import relpath, isfile, join


back_file_dir = relpath("back_files")
rarities = [("Rare", 1),
            ("Uncommon", 20),
            ("Common", 30)]

back_file_dict = {r: [join(back_file_dir, r, f) for f in \
                      listdir(join(back_file_dir, r)) if\
                      isfile(join(back_file_dir, r, f))]\
                            for (r, _) in rarities}
#back_file_list = [fn.rstrip().split(" ") for fn in bf.readlines()]


with open("super_secret_key.txt") as f:
    key = f.readlines()[0].rstrip()


back_bot = Bot("~")

def pick_random_file():
    total = sum(f for r, f in rarities)
    roll = random.randint(1, total)
    acc = 0
    for r, f in rarities:
        acc+=f
        if roll <= acc:
            return pick_random_from_list(back_file_dict[r])
            

def pick_random_from_list(inList):
    return inList[random.randint(0, len(inList) - 1)]

async def nil_corout():
    return


async def play_opus_audio_to_channel_then_leave(message, opus_filename,\
#                                           staytime_seconds = 2,\
                                           failure_coroutine = nil_corout):
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
#           voice_client = await back_bot.join_voice_channel(message.author.voice.voice_channel)
            async def join_the_channel():
                return await asyncio.shield(back_bot.join_voice_channel(\
                                message.author.voice.voice_channel))
                
            voice_client = await join_the_channel()
                    #Play the audio, then disconnect
            try:
                def disconnect_from_vc(*args):
    #                print("after called")
                    fut = asyncio.run_coroutine_threadsafe(voice_client.disconnect(), back_bot.loop)
                    try:
                        fut.result()
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
            
        

    else:
        await failure_coroutine()
    #EXIT
    

@back_bot.event
async def on_read():
    print("Back into action")


message_loop = asyncio.get_event_loop()
@back_bot.event
async def on_message(message):
    if(("back" in message.content.lower()) and (message.author.id != back_bot.user.id)\
       and back_bot.voice_client_in(message.server) == None):
        
        print("back found! " + message.author.name + " is back at " + time.asctime())
        async def say_back_message():
            await back_bot.send_message(message.channel, "Did somebody say back?")
        
        filename = pick_random_file()
        await play_opus_audio_to_channel_then_leave(message, filename,\
                                               failure_coroutine = say_back_message)

    await back_bot.process_commands(message)



@back_bot.command()
async def im_back(*args):
    return await back_bot.say("Hi Back")
@back_bot.command()
async def am_i_back(*args):
    return await back_bot.say("Yes Back, you are Back")
@back_bot.command()
async def bitch(*args):
    return await back_bot.say("I ain't no back bitch")

back_bot.run(key)