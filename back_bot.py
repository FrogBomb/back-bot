import discord
from discord.ext.commands import Bot
import discord.opus as opus
import time

with open("super_secret_key.txt") as f:
    key = f.readlines()[0].rstrip()


back_bot = Bot("~")

async def nil_corout():
    return

async def play_opus_audio_to_channel_then_leave(message, opus_filename,\
                                           staytime_seconds = 2,\
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
        
        #Move to the correct voice channel
        if(back_bot.is_voice_connected(message.author.server)):
            voice_client = back_bot.voice_client_in(message.author.server)
            await voice_client.move_to(message.author.voice.voice_channel)
        else:
            voice_client = await back_bot.join_voice_channel(message.author.voice.voice_channel)
        
        #Play the audio, then disconnect
        try:
            def disconnect_from_vc(*args):
                voice_client.disconnet()
                
            player = voice_client.create_ffmpeg_player(opus_filename, after = disconnect_from_vc)
            
            player.start()
            time.sleep(staytime_seconds)
            await voice_client.disconnect()
            
        except Exception as e:
            await voice_client.disconnect()
            await failure_coroutine()
            raise e
    else:
        await failure_coroutine()
    

@back_bot.event
async def on_read():
    print("Back into action")
    
@back_bot.event
async def on_message(message):
        if(("back" in message.content.lower()) and (message.author.id != back_bot.user.id)):
            print("back found! " + message.author.id + " is back at " + time.asctime())
            
            async def say_back_message():
                await back_bot.send_message(message.channel, "Did somebody say back?")
                
            await play_opus_audio_to_channel_then_leave(message, "did_somebody_say_back.opus",\
                                                   failure_coroutine = say_back_message)

        await back_bot.process_commands(message)
#
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