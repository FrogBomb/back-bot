#import discord
from discord.ext.commands import Bot

with open("super_secret_key.txt") as f:
    key = f.readlines()[0].rstrip()


back_bot = Bot("~")

@back_bot.event
async def on_read():
    print("Back into action")
    
@back_bot.event
async def on_message(message):
    #it's a good bug
        if(("back" in message.content.lower()) and (message.author.id != back_bot.user.id)):
            print("back found!")
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