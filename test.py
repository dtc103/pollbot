import discord
from discord.ext import commands

bot = commands.Bot("!")


async def wait_for_query(ctx, message, delete_after=None):
    accept_emoji = "✅"
    decline_emoji = "❌"

    msg = await ctx.send(message)
    await msg.add_reaction(accept_emoji)
    await msg.add_reaction(decline_emoji)
    reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user and reaction.message.id == msg.id)

    if reaction.emoji == accept_emoji:
        return True
    else:
        return False


@bot.command(name="test")
async def test(ctx):
    if await wait_for_query(ctx, "Willst du?"):
        print("yes")
    else:
        print("No")


bot.run("NjI4OTczNTk3MjcyMTc4Njk4.Xosf-Q.KzpKKxwK-e_tVdKb4QOjoLOS5uw")
