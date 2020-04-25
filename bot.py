import os
import discord
from discord.ext import commands, tasks

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


class PollBotCog(commands.Cog):
    guild_role_uses = {}
    guild_channel_uses = {}
    guild_polls = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.has_any_role()
    @bot_command_channel(channel=BOTCHANNEL)
    @commands.group(name="create")
    async def create(self, ctx):
        if ctx.invoked_subcommand is None:
            print("failure")

    @create.command(name="custom")
    async def create_custom(self, ctx):
        await ctx.send("**Titel für Umfrage festlegen:**")

        try_again_headline = True
        while(try_again_headline):
            msg = await wait_for_message(ctx, None)
            headline = msg.content

            if await wait_for_query(ctx, f"Ist **{headline}** richtig?"):
                try_again_headline = False
                break
            else:
                if await wait_for_query(ctx, "Nochmal versuchen?"):
                    try_again_headline = True
                    await ctx.send("Titel eingeben:")
                    continue
                else:
                    try_again_headline = False
                    return

        itemlist = {}

        add_item = True
        while(add_item):
            msg = await wait_for_message(
                ctx, "**Umfrageoption hinzufügen und mit entsprechendem emoji reagieren:**")
            item_desc = msg.content
            reaction = await wait_for_reaction(ctx, msg)
            item_emoji = reaction.emoji

            if await wait_for_query(ctx, f"Ist {item_emoji} **{item_desc}** richtig?"):
                itemlist[item_emoji] = item_desc

                if await wait_for_query(ctx, "Weitere Option hinzufügen?"):
                    add_item = True
                    continue
                else:
                    add_item = False
                    break
            else:
                if await wait_for_query(ctx, "Nochmal versuchen?"):
                    add_item = True
                    continue
                else:
                    add_item = False
                    break

        description = ""
        if await wait_for_query(ctx, "Soll noch eine Beschreibung hinzugefügt werden?"):
            descritption_ready = True
            while descritption_ready:
                msg = await wait_for_message(ctx, "**Beschreibung:**")
                description = msg.content

                if await wait_for_query(ctx, f"Ist **{description}** richtig?"):
                    descritption_ready = False
                    break
                else:
                    if await wait_for_query(ctx, "Nochmal versuchen?"):
                        descritption_ready = True
                        continue
                    else:
                        descritption_ready = False
                        break

        msg = await wait_for_message(ctx, "**Stunden eingeben, die die Umfrage laufen soll**")
        max_lifetime = int(msg.content)

        channel_to_write = await choose_channel(ctx)

        if len(itemlist) > 0:
            poll = Poll(channel_to_write, itemlist, headline, description,
                        None, lifetime=max_lifetime)
            msg = await channel_to_write.send(embed=poll.get_as_embed())
            poll.id = msg.id
            poll.max_lifetime = max_lifetime
            for emoji in poll.item_list:
                await msg.add_reaction(emoji)
            glob_poll_list.append(poll)
        else:
            await ctx.send("FEHLER! Umfrageliste leer. Umfrage wurde nicht erstellt")

    @create.command(name="automatic")
    async def create_automatic(self, ctx, *args):

        emojilist = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣",
                     "7️⃣", "8️⃣", "9️⃣", "🔟", "🅰", "🅱", "🆒",
                     "🆓", "🅾", "❓", "❗", "🔆", "🔀", "🩺", "💊",
                     "🧬", "🔬", "📡", "🧪", "🧫", "🧰", "🧲", "🏹"]

        in_args = ""
        for string in args:
            in_args += f"{string} "
        args = in_args.split(';')

        items = {}
        for index, item in enumerate(args):
            if index == 0:
                headline = item
            else:
                if item.strip() != "":
                    items[Poll.emojilist[index - 1]] = item

        description = ""
        if await wait_for_query(ctx, "Soll noch eine Beschreibung hinzugefügt werden?"):
            descritption_ready = True
            while descritption_ready:
                msg = await wait_for_message(ctx, "**Beschreibung:**")
                description = msg.content

                if await wait_for_query(ctx, f"Ist **{description}** richtig?"):
                    descritption_ready = False
                    break
                else:
                    if await wait_for_query(ctx, "Nochmal versuchen?"):
                        descritption_ready = True
                        continue
                    else:
                        descritption_ready = False
                        break

        msg = await wait_for_message(ctx, "**Stunden eingeben, die die Umfrage laufen soll**")
        max_lifetime = int(msg.content)

        channel_to_write = await choose_channel(ctx)

        if len(items) > 0:
            poll = Poll(channel_info=channel_to_write, item_list=items, headline=headline,
                        description=description, message_id=None, lifetime=max_lifetime)
            msg = await channel_to_write.send(embed=poll.get_as_embed())
            poll.id = msg.id
            for emoji in poll.item_list:
                await msg.add_reaction(emoji)
            glob_poll_list.append(poll)
        else:
            await ctx.send("FEHLER! Umfrageliste leer. Umfrage wurde nicht erstellt")

    # TODO
    @commands.command(name="help")
    async def help(self, ctx):
        pass

    @commands.has_any_role("Moderator", "Technik-Support", "Administrator")
    @bot_command_channel(channel=BOTCHANNEL)
    @commands.group(name="edit")
    async def edit(self, ctx):
        if ctx.invoked_subcommand is None:
            print("Benutzung:")

    @edit.command(name="commandchannel")
    async def edit_commandchannel(self, ctx, channelname: str):
        BOTCHANNEL = channelname

    @edit.command(name="option")
    async def edit_change(self, ctx):
        poll = await choose_poll(ctx)
        await ctx.send("**Welche Umfrageoption soll geändert werden?**")

        response = "```"
        for index, emoji in enumerate(poll.item_list):
            response += f"{index + 1} : {poll.item_list[emoji]}"
        response += "```"
        await ctx.send(response)
        index = int((await wait_for_message(ctx)).content) - 1

        msg = await wait_for_message(ctx, "**Zu ändernden Text eingeben:**")
        poll.item_list[list(poll.item_list)[index]] = msg.content

        await (await ctx.fetch_message(poll.id)).edit(embed=poll.get_as_embed())

    @edit.command(name="title")
    async def edit_title(self, ctx):
        await ctx.message.delete(delay=20)
        poll = await choose_poll(ctx)

        msg = await wait_for_message(ctx, "**Neuen Titel eingeben**", 20)
        poll.headline = msg.content
        await msg.delete(delay=20)

        message = await ctx.fetch_message(poll.id)

        await message.edit(embed=poll.get_as_embed())

    @edit.command(name="description")
    async def edit_description(self, ctx):
        await ctx.message.delete(delay=20)

        poll = await choose_poll(ctx)

        msg = await wait_for_message(ctx, "**Neue Beschreibung eingeben**", 20)
        poll.description = msg.content
        await msg.delete(delay=20)

        message = await ctx.fetch_message(poll.id)

        await message.edit(embed=poll.get_as_embed())

    @commands.Cog.listener()
    async def on_ready(self):
        await bot.change_presence(activity=discord.Game(name="s?help for usage"),
                                  status=discord.Status.online)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == bot.user:
            return
        for poll in glob_poll_list:
            if reaction.message.id == poll.id:
                poll.add_reaction(reaction)
                await (await reaction.message.channel.fetch_message(poll.id)).edit(embed=poll.get_as_embed())

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        pass

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user == bot.user:
            return
        for poll in glob_poll_list:
            if reaction.message.id == poll.id:
                poll.remove_reaction(reaction)
                await (await reaction.message.channel.fetch_message(poll.id)).edit(embed=poll.get_as_embed())

    async def choose_poll(self, ctx):
        await ctx.send("**Nummer der Umfrage eingeben, die verändert werden soll:**", delete_after=20)
        response = "```"
        for index, poll in enumerate(glob_poll_list):
            response += f"{index + 1}: {poll.headline}\n"
        response += "```"

        msg = await wait_for_message(ctx, response, delete_after=20)
        poll = glob_poll_list[int(msg.content) - 1]
        await msg.delete(delay=20)
        return poll

    async def choose_channel(self, bot, ctx):
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

    def bot_command_channel(self):
        async def wrapper_for_check(ctx, *args):
            command_channels = guild_channel_uses[ctx.guild]
            if len(command_channels) == 0 and command_channels is not None:
                return True

            for channel in command_channels:
                if ctx.message.channel.name == channel:
                    return True

            await ctx.send(f"{ctx.message.author.mention}, this botcommand belongs into {discord.utils.find(lambda c: channel == c.name, ctx.message.guild.channels).mention}", delete_after=20)
            await ctx.message.delete(delay=20)

            return False

        return commands.check(wrapper_for_check)

    def get_guild_from_context(self, ctx):
        return ctx.guild


# ctx = channelcontext, msg = message, that should be reacted on


##########################################################################################

bot.run(TOKEN)
