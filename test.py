import discord
from discord.ext import commands

import dotenv
from dotenv import load_dotenv

import os

bot = commands.Bot(command_prefix="!")

load_dotenv()

TOKEN = os.getenv("TOKEN")

@bot.event
async def on_ready():
    game = discord.Game("!help")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("Ready")

@bot.command(name="test")
async def test(ctx):
    pass

bot.run(TOKEN)
