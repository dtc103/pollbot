import discord
from discord.ext import commands

import dotenv
from dotenv import load_dotenv

import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot("!")


async def wait_for_message(ctx, message=None, delete_after=None):
    if message is None:
        return await bot.wait_for(event='message', check=lambda message: ctx.author == message.author)
    else:
        await ctx.send(message, delete_after=delete_after)
        return await bot.wait_for(event='message', check=lambda message: ctx.author == message.author)


async def choose_channel(ctx):
    await ctx.send("**In welchen Channel soll die Umfrage gestellt werden?**")
    guild = discord.utils.find(lambda g: ctx.guild == g, bot.guilds)
    response = "```"
    for index, channel in enumerate(guild.text_channels):
        response += f"{index + 1}: {channel.name}\n"
    response += "```"

    await ctx.send(response)

    msg = await wait_for_message(ctx)
    index = int(msg.content)

    return guild.text_channels[index - 1]


@bot.command(name="test")
async def test(ctx):
    channel = await choose_channel(ctx)
    print(channel.name)


bot.run(TOKEN)
