import discord
from discord.ext import tasks, commands
from discordPoll import DiscordPoll, get_poll_as_embed
from utilities import *


class PollBotCog(commands.Cog):
    # key is the guild, value is a list
    guild_role_uses = {}
    guild_channel_uses = {}
    guild_polls = {}

    def __init__(self, bot):
        self.bot = bot

    #@has_server_role(guild_role_uses)
    #@bot_command_channel(guild_channel_uses)
    @commands.group(name="create")
    async def create(self, ctx):
        if ctx.invoked_subcommand is None:
            #normally print help here
            print("failure")
        else:
            if ctx.guild not in self.guild_polls:
                self.guild_polls[ctx.guild] = []

    @create.command(name="custom")
    async def create_custom(self, ctx):
        try_again_headline = True
        while(try_again_headline):
            msg = await wait_for_message(self.bot, ctx, "**Titel für Umfrage festlegen:**")
            headline = msg.content

            if await wait_for_query(self.bot, ctx, f"Ist **{headline}** richtig?"):
                try_again_headline = False
                break
            else:
                if await wait_for_query(self.bot, ctx, "Nochmal versuchen?"):
                    try_again_headline = True
                    continue
                else:
                    try_again_headline = False
                    await ctx.send("Titel wird benötgt. Umfrage wurde nicht erstellt")
                    return

        items = {}
        add_item = True
        while(add_item):
            msg = await wait_for_message(self.bot,
                                         ctx, "**Umfrageoption hinzufügen und mit entsprechendem emoji auf die Option reagieren:**")
            item_desc = msg.content
            reaction = await wait_for_reaction(self.bot, ctx, msg)
            item_emoji = reaction.emoji

            if await wait_for_query(self.bot, ctx, f"Ist {item_emoji} **{item_desc}** richtig?", None):
                items[item_emoji] = item_desc

                if await wait_for_query(self.bot, ctx, "Weitere Option hinzufügen?", None):
                    add_item = True
                    continue
                else:
                    add_item = False
                    break
            else:
                if await wait_for_query(self.bot, ctx, "Nochmal versuchen?"):
                    add_item = True
                    continue
                else:
                    if len(items) < 1:
                        await ctx.send("Umfrageliste leer. Umfrage wurde nicht erstellt")
                        add_item = False
                        return
                    add_item = False
                    break

        description = None
        if await wait_for_query(self.bot, ctx, "Soll noch eine Beschreibung hinzugefügt werden?"):
            descritption_ready = True
            while descritption_ready:
                msg = await wait_for_message(self.bot, ctx, "**Beschreibung:**")
                description = msg.content

                if await wait_for_query(self.bot, ctx, f"Ist **{description}** richtig?"):
                    descritption_ready = False
                    break
                else:
                    if await wait_for_query(self.bot, ctx, "Nochmal versuchen?"):
                        descritption_ready = True
                        continue
                    else:
                        descritption_ready = False
                        break

        
        time = []
        lifetime = None
        while len(time) != 3:
            msg = await wait_for_message(self.bot, ctx, "**Umfragezeit im Format DD:HH:MM eingeben:**")
            time = msg.content.strip().split(":")

            if len(time) == 3:
                lifetime = int(time[2]) + int(time[1]) * 60 + int(time[0]) * 60 * 24
                break

            await ctx.send("Zeitformat falsch eingegeben")

            if await wait_for_query(self.bot, ctx, "Umfragezeit nochmal eingeben?"):
                continue
            else:
                await ctx.send("Es wurde keine Zeit eingegeben")
                break
          
        channel_to_write = await choose_channel(self.bot, ctx, ctx.guild)

        #create poll and send to channel
        poll = DiscordPoll(items, headline, ctx.guild, channel_to_write, description=description if description is not None else None, lifetime=lifetime if lifetime is not None else None)
        msg = await channel_to_write.send(embed=get_poll_as_embed(poll))
        for emoji in poll.item_list:
            await msg.add_reaction(emoji)
        self.guild_polls[ctx.guild].append(poll)
        poll.start(msg)

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
                    items[emojilist[index - 1]] = item

        description = ""
        if await wait_for_query(self.bot, ctx, "Soll noch eine Beschreibung hinzugefügt werden?"):
            descritption_ready = True
            while descritption_ready:
                msg = await wait_for_message(self.bot, ctx, "**Beschreibung:**")
                description = msg.content

                if await wait_for_query(self.bot, ctx, f"Ist **{description}** richtig?"):
                    descritption_ready = False
                    break
                else:
                    if await wait_for_query(self.bot, ctx, "Nochmal versuchen?"):
                        descritption_ready = True
                        continue
                    else:
                        descritption_ready = False
                        break

        time = []
        lifetime = None
        while len(time) != 3:
            msg = await wait_for_message(self.bot, ctx, "**Umfragezeit im Format DD:HH:MM eingeben:**")
            time = msg.content.strip().split(":")

            if len(time) == 3:
                lifetime = int(time[2]) + int(time[1]) * 60 + int(time[0]) * 60 * 24
                break

            await ctx.send("Zeitformat falsch eingegeben")

            if await wait_for_query(self.bot, ctx, "Umfragezeit nochmal eingeben?"):
                continue
            else:
                await ctx.send("Es wurde keine Zeit eingegeben")
                break

        channel_to_write = await choose_channel(self.bot, ctx, ctx.guild)

        if len(items) > 0:
            poll = DiscordPoll(items, headline, ctx.guild, channel_to_write, description=description if description is not None else None, lifetime=lifetime if lifetime is not None else None)
            msg = await channel_to_write.send(embed=get_poll_as_embed(poll))
            for emoji in poll.item_list:
                await msg.add_reaction(emoji)
            self.guild_polls[ctx.guild].append(poll)
            poll.start(msg)
        else:
            await ctx.send("FEHLER! Umfrageliste leer. Umfrage wurde nicht erstellt")

    # TODO
    @commands.command(name="help")
    async def help(self, ctx):
        pass

    #@has_server_role(guild_role_uses)
    #@bot_command_channel(guild_channel_uses)
    @commands.group(name="edit")
    async def edit(self, ctx):
        if ctx.invoked_subcommand is None:
            print("Benutzung:")

    @edit.command(name="commandchannel")
    async def edit_commandchannel(self, ctx, channelname: str):
        pass

    @edit.command(name="option")
    async def edit_change(self, ctx):
        poll = await self.choose_poll(ctx)
        await ctx.send("**Welche Umfrageoption soll geändert werden?**")

        response = "```"
        for index, emoji in enumerate(poll.item_list):
            response += f"{index + 1} : {poll.item_list[emoji]}"
        response += "```"
        await ctx.send(response)
        index = int((await wait_for_message(self.bot, ctx)).content) - 1

        msg = await wait_for_message(ctx, "**Zu ändernden Text eingeben:**")
        poll.item_list[list(poll.item_list)[index]] = msg.content

        await (await ctx.fetch_message(poll.id)).edit(embed=poll.get_as_embed())

    @edit.command(name="title")
    async def edit_title(self, ctx):
        await ctx.message.delete(delay=20)
        poll = await self.choose_poll(ctx)

        msg = await wait_for_message(ctx, "**Neuen Titel eingeben**", 20)
        poll.headline = msg.content
        await msg.delete(delay=20)

        message = await ctx.fetch_message(poll.id)

        await message.edit(embed=get_poll_as_embed(poll))

    @edit.command(name="description")
    async def edit_description(self, ctx):
        await ctx.message.delete(delay=20)

        poll = await self.choose_poll(ctx)

        msg = await wait_for_message(ctx, "**Neue Beschreibung eingeben**", 20)
        poll.description = msg.content
        await msg.delete(delay=20)

        message = await ctx.fetch_message(poll.id)

        await message.edit(embed=poll.get_as_embed())

    ######################### LISTENER #######################################
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.guild_channel_uses[guild] = []
        self.guild_polls[guild] = []
        self.guild_role_uses[guild] = []

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name="s?help for usage"),
                                       status=discord.Status.online)
    

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return
        # for poll in self.guild_polls[reaction.message.guild]:
        #     if reaction.message.id == poll.id:
        #         poll.add_reaction(reaction)
        #         await (await reaction.message.channel.fetch_message(poll.id)).edit(embed=poll.get_as_embed())

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user == self.bot.user:
            return
        # for poll in self.guild_polls[reaction.message.guild]:
        #     if reaction.message.id == poll.id:
        #         poll.remove_reaction(reaction)
        #         await (await reaction.message.channel.fetch_message(poll.id)).edit(embed=poll.get_as_embed())

    async def choose_poll(self, ctx):
        await ctx.send("**Nummer der Umfrage eingeben, die verändert werden soll:**", delete_after=20)
        response = "```"
        # for index, poll in enumerate(glob_poll_list):
        #     response += f"{index + 1}: {poll.headline}\n"
        # response += "```"

        msg = await wait_for_message(ctx, response, delete_after=20)
        #poll = glob_poll_list[int(msg.content) - 1]
        await msg.delete(delay=20)
        # return poll
        return    

def bot_command_channel(guild_command_channel):
    async def wrapper_for_check(ctx, *args):
        command_channels = guild_command_channel[ctx.guild]
        if len(command_channels) == 0 and command_channels is not None:
            return True

        for channel in command_channels:
            if ctx.message.channel == channel:
                return True

        await ctx.send(f"{ctx.message.author.mention}, this botcommand belongs into {discord.utils.find(lambda c: channel == c.name, ctx.message.guild.channels).mention}", delete_after=20)
        await ctx.message.delete(delay=20)

        return False

    return commands.check(wrapper_for_check)

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

    return commands.check(has_any_role)

def get_guild_from_context(ctx):
    return ctx.guild
