import discord
from discord.ext import commands, tasks
import asyncio

import dotenv
from dotenv import load_dotenv

import os

from poll import Poll
from discordPoll import DiscordPoll

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="!")

def has_server_role(guild_command_roles):
    async def has_any_role(ctx, *args):
        for guild in guild_command_roles:
            if guild == ctx.guild:
                accepted_roles = guild_command_roles[guild]
                if len(accepted_roles) < 1:
                    return True 
                for role in accepted_roles:
                    for member_role in ctx.message.author.roles:
                        if role == member_role:
                            return True
                return False
        return False

    return commands.check(has_any_role)

#@has_server_role({"Jackbox Party Server": []})
@bot.command(name="test")
async def test(ctx):
    print("can access")

bot.run(TOKEN)