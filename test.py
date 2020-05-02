import discord
from discord.ext import commands, tasks
import asyncio

import dotenv
from dotenv import load_dotenv

import os

from poll import Poll
from discordPoll import DiscordPoll

from help_embeds import get_help_german

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="t!")


@bot.command(name="test")
async def test(ctx):
    await ctx.send(embed=get_help_german())


bot.run(TOKEN)
