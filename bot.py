import os
import discord
from discord.ext import commands, tasks

from discordPoll import DiscordPoll
from pollBotCog import PollBotCog

from utilities import *

import dotenv
from dotenv import load_dotenv

import asyncio

import datetime

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOTCHANNEL = os.getenv("BOTCHANNEL")

bot = commands.Bot(command_prefix="s?")
bot.remove_command("help")

glob_poll_list = []


# ctx = channelcontext, msg = message, that should be reacted on

##########################################################################################
bot.add_cog(PollBotCog(bot))
bot.run(TOKEN)
