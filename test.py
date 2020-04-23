import discord
from discord.ext import commands, tasks

import dotenv
from dotenv import load_dotenv

import os

from poll import Poll
from discordPoll import DiscordPoll

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="!")



bot.run(TOKEN)