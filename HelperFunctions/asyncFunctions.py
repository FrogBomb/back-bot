from BotGlobals import BACK_BOT, RARITY_COLORS
from .embedHelpers import back_embed
import discord
import discord.opus as opus
import asyncio
from os.path import split

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
    possible. Then, will play the audio file.

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
        em = back_embed(clip, rarity, rarity_colors, back_bot, message.author.name)
        await back_bot.send_message(message.channel, embed=em)
        if(give_loot):
            back_bot.lootTracker(message.author, rarity, clip)

    else:
        await failure_coroutine()
    #EXIT
