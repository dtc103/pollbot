import os
import discord
from discord.ext import commands, tasks

import dotenv
from dotenv import load_dotenv


import asyncio

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="umf!")
bot.remove_command("help")

glob_poll_list = []


class Poll:
    emojilist = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣",
                 "7️⃣", "8️⃣", "9️⃣", "🔟", "🅰", "🅱", "🆒",
                 "🆓", "🅾", "❓", "❗", "🔆", "🔀", "🩺", "💊",
                 "🧬", "🔬", "📡", "🧪", "🧫", "🧰", "🧲", "🏹"]

    def __init__(self, item_list: {}, headline: str, description: str, message_id):
        self.item_list = item_list
        self.headline = headline
        self.description = description
        self.id = message_id

    def __str__(self):
        pass

    def get_as_embed(self):
        embed = discord.Embed(title=self.headline,
                              colour=discord.Colour.blue())
        if self.description is not None:
            embed.description = self.description
        for key in self.item_list:
            embed.add_field(
                name='\u200b', value=f"{key}: {self.item_list[key]}", inline=False)
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


##########################################################################################

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

    if len(itemlist) > 0:
        poll = Poll(itemlist, headline, description, None)
        msg = await ctx.send(embed=poll.get_as_embed())
        poll.id = msg.id
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

    if len(items) > 0:
        poll = Poll(item_list=items, headline=headline,
                    description=description, message_id=None)
        msg = await ctx.send(embed=poll.get_as_embed())
        poll.id = msg.id
        for emoji in poll.item_list:
            await msg.add_reaction(emoji)
        glob_poll_list.append(poll)
    else:
        await ctx.send("FEHLER! Umfrageliste leer. Umfrage wurde nicht erstellt")


@bot.event
async def on_reaction_add(reaction, user):
    print(reaction.emoji)
    print("add")


@bot.event
async def on_reaction_remove(reaction, user):
    print(reaction.emoji)
    print("remove")


@bot.command(name="help")
async def help(ctx):
    pass


@bot.group(name="edit")
async def edit(ctx):
    if ctx.invoked_subcommand is None:
        print("Benutzung:")


@edit.command(name="option")
async def edit_change(ctx):
    poll = await choose_poll(ctx)
    await ctx.send("**Welche Umfrageoption soll geändert werden?**")
    poll_optionlist = (await ctx.fetch_message(poll.id)).embeds[0].fields

    response = "```"
    for index, embed_item in enumerate(poll_optionlist):
        response += f"{index + 1} : \"{str(embed_item.value)}\"\n"
    response += "```"
    await ctx.send(response)
    index = int((await wait_for_message(ctx)).content) - 1

    change_correct = True
    new_option_text = None
    while change_correct:
        msg = await wait_for_message(ctx, "**Zu ändernden Text eingeben:**")
        if await wait_for_query(ctx, f"Ist **{msg.content}** richtig?"):
            change_correct = False
            new_option_text = msg.content
        else:
            if await wait_for_query(ctx, "Nochmal versuchen?"):
                change_correct = True
            else:
                change_correct = False

    value = poll_optionlist[index].value
    for item in poll.item_list:
        if value.startswith(item):
            poll.item_list[item] = new_option_text

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
