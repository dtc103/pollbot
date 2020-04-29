import discord
from discord.ext import tasks, commands
from discordPoll import DiscordPoll
from utilities import *


class PollBotCog(commands.Cog):
    # key is the guild, value is a list
    guild_role_uses = {}
    guild_channel_uses = {}
    guild_polls = {}

    def __init__(self, bot):
        self.bot = bot

    # @has_server_role()
    # @bot_command_channel()
    @commands.group(name="create")
    async def create(self, ctx):
        if ctx.invoked_subcommand is None:
            print("failure")

    @create.command(name="custom")
    async def create_custom(self, ctx):
        await ctx.send("**Titel für Umfrage festlegen:**")

        try_again_headline = True
        while(try_again_headline):
            msg = await wait_for_message(self.bot, ctx, None)
            headline = msg.content

            if await wait_for_query(self.bot, ctx, f"Ist **{headline}** richtig?"):
                try_again_headline = False
                break
            else:
                if await wait_for_query(self.bot, ctx, "Nochmal versuchen?"):
                    try_again_headline = True
                    await ctx.send("Titel eingeben:")
                    continue
                else:
                    try_again_headline = False
                    return

        itemlist = {}

        add_item = True
        while(add_item):
            msg = await wait_for_message(self.bot,
                                         ctx, "**Umfrageoption hinzufügen und mit entsprechendem emoji reagieren:**", None)
            item_desc = msg.content
            reaction = await wait_for_reaction(self.bot, ctx, msg)
            item_emoji = reaction.emoji

            if await wait_for_query(self.bot, ctx, f"Ist {item_emoji} **{item_desc}** richtig?", None):
                itemlist[item_emoji] = item_desc

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

        msg = await wait_for_message(self.bot, ctx, "**Stunden eingeben, die die Umfrage laufen soll**")
        max_lifetime = int(msg.content)

        channel_to_write = await self.choose_channel(self.bot, ctx, "Choose Channel")

        if len(itemlist) > 0:
            poll = DiscordPoll(itemlist, headline, None,
                               None, ctx.guild, description=description if description != "" else None, lifetime=max_lifetime * 60)
            msg = await channel_to_write.send(embed=poll.get_as_embed())
            poll.id = msg.id
            poll.channel = msg.channel
            for emoji in poll.item_list:
                await msg.add_reaction(emoji)
            self.guild_polls[ctx.guild].append(poll)
            poll.start()
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
            poll = DiscordPoll(items, headline, None, None,
                               description=description if description != "" else None, lifetime=max_lifetime*60)
            msg = await channel_to_write.send(embed=poll.get_as_embed())
            poll.id = msg.id
            poll.channel = msg.channel
            for emoji in poll.item_list:
                await msg.add_reaction(emoji)
            self.guild_polls[ctx.guild].append(poll)
            poll.start
        else:
            await ctx.send("FEHLER! Umfrageliste leer. Umfrage wurde nicht erstellt")

    # TODO
    @commands.command(name="help")
    async def help(self, ctx):
        pass

    # @has_server_role()
   # @bot_command_channel()
    @commands.group(name="edit")
    async def edit(self, ctx):
        if ctx.invoked_subcommand is None:
            print("Benutzung:")

    @edit.command(name="commandchannel")
    async def edit_commandchannel(self, ctx, channelname: str):
        pass

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

    ######################### LISTENER #######################################
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.guild_channel_uses[guild] = []
        self.guild_polls[guild] = []
        self.guild_role_uses = []

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

    async def choose_channel(self, bot, ctx, msg=None):
        await ctx.send(msg)
        guild = discord.utils.find(lambda g: ctx.guild == g, bot.guilds)
        response = "```"
        for index, channel in enumerate(guild.text_channels):
            response += f"{index + 1}: {channel.name}\n"
        response += "```"

        await ctx.send(response)

        msg = await wait_for_message(self.bot, ctx)
        index = int(msg.content)

        return guild.text_channels[index - 1]

    def get_poll_as_embed(self, poll: DiscordPoll):
        embed = discord.Embed(title=self.headline,
                              colour=discord.Colour.blue())

        if poll.description is not None:
            embed.description = self.description
        for key in poll.item_list:
            embed.add_field(
                name='\u200b', value=f"{key}: {self.item_list[key]}", inline=False)
        if poll.highest_item is not None:
            embed.add_field(
                name='\u200b', value=f"**Most votes**: {self.item_list[self.highest_item]}")

        embed.set_thumbnail(url=poll.guild.icon_url)

        days_left = int((self.lifetime / 60) / 24)
        hours_left = int(self.lifetime / 60) - 24 * days_left
        minutes_left = int(self.lifetime - days_left *
                           24 * 60 - hours_left * 60)

        if days_left < 10:
            days_left_string = f"0{days_left}"
        else:
            days_left_string = f"{days_left}"
        if hours_left < 10:
            hours_left_string = f"0{hours_left}"
        else:
            hours_left_string = f"{hours_left}"
        if minutes_left < 10:
            minutes_left_string = f"0{minutes_left}"
        else:
            minutes_left_string = f"{minutes_left}"

        embed.set_footer(
            text=f"Time left: {days_left_string}:{hours_left_string}:{minutes_left_string}")

        return embed

    # def bot_command_channel(self):
    #     async def wrapper_for_check(ctx, *args):
    #         command_channels = guild_channel_uses[ctx.guild]
    #         if len(command_channels) == 0 and command_channels is not None:
    #             return True

    #         for channel in command_channels:
    #             if ctx.message.channel == channel:
    #                 return True

    #         await ctx.send(f"{ctx.message.author.mention}, this botcommand belongs into {discord.utils.find(lambda c: channel == c.name, ctx.message.guild.channels).mention}", delete_after=20)
    #         await ctx.message.delete(delay=20)

    #         return False

    #     return commands.check(wrapper_for_check)

    # def has_server_role(self):

    #     async def get_roles(ctx, *args):
    #         for guild in self.bot.guilds:
    #             if ctx.guild == guild:
    #                 return self.guild_role_uses[guild]

    #     return commands.check(commands.has_any_role(get_roles))

    # def get_guild_from_context(self, ctx):
    #     return ctx.guild
