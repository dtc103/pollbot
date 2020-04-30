import os
import asyncio
import discord
from discord.ext import commands, tasks

import dotenv
from dotenv import load_dotenv

from pollBotCog import PollBotCog

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
