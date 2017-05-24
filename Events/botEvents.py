from BotGlobals import  BACK_BOT,\
                        CMD_PREFIX,\
                        RARITIES,\
                        BACK_FILE_DIR,\
                        BACK_FILE_DICT,\
                        ROLLBACK_THRESHOLD

from HelperFunctions.asyncFunctions import play_opus_audio_to_channel_then_leave
from HelperFunctions.randomizers import pick_random_file
import time

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
    back_to_play = " ".join((message.content).split(" ")[1:]).strip()
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

# @BACK_BOT.command(pass_context=True)
# async def give(context):
#     message = context.message
#     try:
#         what_back, to_who = [w.strip() for w in " ".join((message.content).split(" ")[1:]).split("->")]
#     except ValueError:
#         return await BACK_BOT.say(_help_on_give(CMD_PREFIX + "give"))
#     lootTracker = BACK_BOT.lootTracker
#     player = message.author.name
#     if player in lootTracker.players_to_loot:
#         giving_players_lootBag = lootTracker.players_to_loot[player]
#         rarity = giving_players_lootBag.rm_loot(what_back)
#         if rarity != None:
#             lootTracker.add_loot(to_who, rarity, what_back)
#             return await BACK_BOT.say(\
#                             "{p} gave back {back} to {friend}!".format(\
#                                       p=player, back=what_back, friend=to_who))
#         else:
#             return await BACK_BOT.say("You don't have that back!")
#     else:
#         return await BACK_BOT.say("You haven't even hit the back ~board!")
#
# def _help_on_give(commandToGive):
#     return "To give back: ```\n{cmd} my_back.mp4 -> UserNameOfFriend\n```".format(cmd=commandToGive)
