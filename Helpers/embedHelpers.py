import discord
def back_embed(clip, rarity, rarity_colors, back_bot, player):
            color = rarity_colors[rarity]
            em = discord.Embed(title= rarity + " :back: for " +player,\
                               description = clip,\
                               color=color)
            em.set_author(name='Back Bot', icon_url=back_bot.user.avatar_url)
            return em
