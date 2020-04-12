import discord
from discord.ext import commands

import dotenv
from dotenv import load_dotenv

import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

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
    embed = discord.Embed(title="title")
    embed.add_field(name="name1", value="val1")
    embed.add_field(name="name2", value="val2")
    msg = await ctx.send(embed=embed)

    msg = await ctx.fetch_message(msg.id)
    embed = msg.embeds[0]
    print(embed.fields[0].name)
    embed.fields[0].name = "carlos"
    print(embed.fields[0].name)

    # await ctx.send(embed=embed)


bot.run(TOKEN)
