import os
import discord
from discord.ext import commands, tasks

import dotenv
from dotenv import load_dotenv


import asyncio

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="g!")
bot.remove_command("help")

glob_poll_list = []


class Poll:
    def __init__(self, items_list: {}, headline: str, message_id):
        self.item_list = items_list
        self.headline = headline
        self.id = message_id

    def __str__(self):
        pass


@bot.command(name="create")
async def create_poll(ctx):
    accept_emoji = "✅"
    decline_emoji = "❌"

    await ctx.send("**Titel für Umfrage festlegen:**")

    try_again_headline = True
    while(try_again_headline):
        msg = await bot.wait_for(event='message', check=lambda message: ctx.author == message.author)
        headline = msg.content

        msg = await ctx.send(f"Ist **{headline}** richtig?")
        await msg.add_reaction(accept_emoji)
        await msg.add_reaction(decline_emoji)

        reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user)
        if reaction.emoji == accept_emoji:
            try_again_headline = False
        else:
            msg = await ctx.send("Nochmal versuchen?")
            await msg.add_reaction(accept_emoji)
            await msg.add_reaction(decline_emoji)
            reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user)

            if reaction.emoji == accept_emoji:
                try_again_headline = True
                await ctx.send("Titel eingeben:")
                continue
            else:
                try_again_headline = False
                break

    itemlist = {}

    add_item = True
    while(add_item):
        await ctx.send("**Umfrageoption hinzufügen und mit entsprechendem emoji reagieren:**")

        msg = await bot.wait_for("message", check=lambda message: ctx.author == message.author)
        item_desc = msg.content
        reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user)
        item_emoji = reaction.emoji

        msg = await ctx.send(f"Ist **{item_emoji} {item_desc}** richtig?")
        await msg.add_reaction(accept_emoji)
        await msg.add_reaction(decline_emoji)
        reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user)

        if reaction.emoji == accept_emoji:
            itemlist[item_emoji] = item_desc

            msg = await ctx.send("Weitere Option hinzufügen?")
            await msg.add_reaction(accept_emoji)
            await msg.add_reaction(decline_emoji)
            reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user)

            if reaction.emoji == accept_emoji:
                add_item = True
                continue
            else:
                add_item = False
                break

        else:
            msg = await ctx.send("Nochmal versuchen?")
            await msg.add_reaction(accept_emoji)
            await msg.add_reaction(decline_emoji)
            reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user)

            if reaction.emoji == accept_emoji:
                add_item = True
                continue
            else:
                add_item = False
                break

    embed = discord.Embed(title=headline, colour=discord.Colour.blue())
    for key in itemlist:
        embed.add_field(
            name='\u200b', value=f"**{key}**: {itemlist[key]}", inline=False)

    msg = await ctx.send(embed=embed)
    if len(itemlist) != 0:
        glob_poll_list.append(Poll(itemlist, headline, msg.id))


@bot.command(name="help")
async def help(ctx):
    pass

bot.run(TOKEN)
