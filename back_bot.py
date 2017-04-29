import discord
from discord.ext.commands import Bot
import discord.opus as opus
import time

with open("super_secret_key.txt") as f:
    key = f.readlines()[0].rstrip()


back_bot = Bot("~")

@back_bot.event
async def on_read():
    print("Back into action")
    
@back_bot.event
async def on_message(message):
        if(("back" in message.content.lower()) and (message.author.id != back_bot.user.id)):
            print("back found!")
            if(opus.is_loaded() and isinstance(message.author, discord.Member) and message.author.voice.voice_channel != None):
                try:
                    voice_client = await back_bot.join_voice_channel(message.author.voice.voice_channel)
                except:
                    voice_client = back_bot.voice_client_in(message.author.server)
                    await voice_client.move_to(message.author.voice.voice_channel)
                
                try:
                    def disconnect_from_vc(*args):
                        voice_client.disconnet()
                        
                    player = voice_client.create_ffmpeg_player('did_sombody_say_back.opus', after = disconnect_from_vc)
                    
                    player.start()
                    time.sleep(2)
                    await voice_client.disconnect()
                    
                except Exception as e:
                    await voice_client.disconnect()
                    await back_bot.send_message(message.channel, "Did somebody say back?")
                    raise e
            else:
                await back_bot.send_message(message.channel, "Did somebody say back?")
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