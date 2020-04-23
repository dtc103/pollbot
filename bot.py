import os
import discord
from discord.ext import commands, tasks

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


class Poll:
    emojilist = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣",
                 "7️⃣", "8️⃣", "9️⃣", "🔟", "🅰", "🅱", "🆒",
                 "🆓", "🅾", "❓", "❗", "🔆", "🔀", "🩺", "💊",
                 "🧬", "🔬", "📡", "🧪", "🧫", "🧰", "🧲", "🏹"]

    #lifetime in minutes
    def __init__(self, channel_info: discord.TextChannel, item_list: {}, headline: str, description: str, message_id, lifetime: int = 2):
        self.item_list = item_list
        self.headline = headline
        self.description = description
        self.id = message_id
        self.emoji_count = {}
        for key in self.item_list:
            self.emoji_count[key] = 1
        self.highest_count = 1
        self.highest_emoji = None
        self.max_lifetime = lifetime
        self.current_lifetime = 0
        self.channel = channel_info
        self.image = None
        asyncio.create_task(self.lifetime_check())

    async def lifetime_check(self):
        while True:
            print(f"now:{self.current_lifetime} target:{self.max_lifetime}")
            self.current_lifetime += 1
            if self.current_lifetime >= self.max_lifetime:
                if self.highest_emoji == None:
                    await self.channel.send(f"Leider hat keiner bei der Umfrage mitgemacht")
                    break
                else:
                    await self.channel.send(f"Gewonnen hat: **{self.item_list[self.highest_emoji]}** mit **{self.emoji_count[self.highest_emoji]}** Stimmen")
                    glob_poll_list.remove(self)
                    break
            await asyncio.sleep(3600)  # sleep for one hour

    def __str__(self):
        return "__str__(): not implemented"

    def add_reaction(self, reaction):
        for emoji in self.item_list:
            if emoji == reaction.emoji:
                self.emoji_count[emoji] += 1
                if self.emoji_count[emoji] > self.highest_count:
                    self.highest_count = self.emoji_count[emoji]
                    self.highest_emoji = emoji

    def remove_reaction(self, reaction):
        for emoji in self.item_list:
            if emoji == reaction.emoji:
                self.emoji_count[emoji] -= 1
                # if the current emoji was the most voted, find out the new most voted one
                if self.highest_emoji == emoji:
                    self.highest_count -= 1
                    highest_emoji = None
                    highest_count = 1
                    for new_emoji in self.item_list:
                        if self.emoji_count[new_emoji] > highest_count:
                            highest_count = self.emoji_count[new_emoji]
                            highest_emoji = new_emoji
                    if highest_emoji is not None:
                        self.highest_emoji = highest_emoji
                    self.highest_count = highest_count

    def update_highest(self, emoji, count):
        self.max_emoji = emoji
        self.max_count = count

    def get_as_embed(self):
        embed = discord.Embed(title=self.headline,
                              colour=discord.Colour.blue())
        if self.description is not None:
            embed.description = self.description
        for key in self.item_list:
            embed.add_field(
                name='\u200b', value=f"{key}: {self.item_list[key]}", inline=False)
        if self.highest_emoji is not None:
            embed.add_field(
                name='\u200b', value=f"**Meiste Stimmen**: {self.item_list[self.highest_emoji]}")
        # FIXME please change dis
        for guild in bot.guilds:
            if self.channel.guild == guild:
                embed.set_thumbnail(url=guild.icon_url)
                break
        embed.set_footer(
            text=f"Umfrageende am {str(datetime.datetime.now() + datetime.timedelta(hours = self.max_lifetime))[0:16]}")

        return embed


async def wait_for_message(ctx, message=None, delete_after=None):
    if message is None:
        return await bot.wait_for(event='message', check=lambda message: ctx.author == message.author)
    else:
        await ctx.send(message, delete_after=delete_after)
        return await bot.wait_for(event='message', check=lambda message: ctx.author == message.author)


async def wait_for_query(ctx, message, delete_after=None):
    accept_emoji = "✅"
    decline_emoji = "❌"

    msg = await ctx.send(message, delete_after=delete_after)
    await msg.add_reaction(accept_emoji)
    await msg.add_reaction(decline_emoji)
    reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user and reaction.message.id == msg.id)
    await msg.delete(delay=delete_after)

    if reaction.emoji == accept_emoji:
        return True
    else:
        return False

# ctx = channelcontext, msg = message, that should be reacted on


async def wait_for_reaction(ctx, message=None, delete_after=None):
    reaction, _ = await bot.wait_for(event='reaction_add', check=lambda reaction, user: ctx.author == user and reaction.message.id == message.id)
    return reaction


async def choose_poll(ctx):
    await ctx.send("**Nummer der Umfrage eingeben, die verändert werden soll:**", delete_after=20)
    response = "```"
    for index, poll in enumerate(glob_poll_list):
        response += f"{index + 1}: {poll.headline}\n"
    response += "```"

    msg = await wait_for_message(ctx, response, delete_after=20)
    poll = glob_poll_list[int(msg.content) - 1]
    await msg.delete(delay=20)
    return poll


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


def bot_command_channel(channel=BOTCHANNEL):
    async def wrapper_for_check(ctx, *args):
        if ctx.message.channel.name != channel:
            await ctx.send(f"{ctx.message.author.mention}, this botcommand belongs into {discord.utils.find(lambda c: channel == c.name, ctx.message.guild.channels).mention}", delete_after=20)
            await ctx.message.delete(delay=20)

            return False
        else:
            return True

    return commands.check(wrapper_for_check)

##########################################################################################


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="s?help for usage"),
                              status=discord.Status.online)


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    for poll in glob_poll_list:
        if reaction.message.id == poll.id:
            poll.add_reaction(reaction)
            await (await reaction.message.channel.fetch_message(poll.id)).edit(embed=poll.get_as_embed())


@bot.event
async def on_reaction_remove(reaction, user):
    if user == bot.user:
        return
    for poll in glob_poll_list:
        if reaction.message.id == poll.id:
            poll.remove_reaction(reaction)
            await (await reaction.message.channel.fetch_message(poll.id)).edit(embed=poll.get_as_embed())


@commands.has_any_role("Moderator", "Technik-Support", "Administrator")
@bot_command_channel(channel=BOTCHANNEL)
@bot.group(name="create")
async def create(ctx):
    if ctx.invoked_subcommand is None:
        print("failure")


@create.command(name="custom")
async def create_custom(ctx):
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
async def create_automatic(ctx, *args):
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
@bot.command(name="help")
async def help(ctx):
    pass


@commands.has_any_role("Moderator", "Technik-Support", "Administrator")
@bot_command_channel(channel=BOTCHANNEL)
@bot.group(name="edit")
async def edit(ctx):
    if ctx.invoked_subcommand is None:
        print("Benutzung:")


@edit.command(name="commandchannel")
async def edit_commandchannel(ctx, channelname: str):
    BOTCHANNEL = channelname


@edit.command(name="option")
async def edit_change(ctx):
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
async def edit_title(ctx):
    await ctx.message.delete(delay=20)
    poll = await choose_poll(ctx)

    msg = await wait_for_message(ctx, "**Neuen Titel eingeben**", 20)
    poll.headline = msg.content
    await msg.delete(delay=20)

    message = await ctx.fetch_message(poll.id)

    await message.edit(embed=poll.get_as_embed())


@edit.command(name="description")
async def edit_description(ctx):
    await ctx.message.delete(delay=20)

    poll = await choose_poll(ctx)

    msg = await wait_for_message(ctx, "**Neue Beschreibung eingeben**", 20)
    poll.description = msg.content
    await msg.delete(delay=20)

    message = await ctx.fetch_message(poll.id)

    await message.edit(embed=poll.get_as_embed())

bot.run(TOKEN)
