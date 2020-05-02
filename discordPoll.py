import discord
from discord.ext import tasks, commands
import asyncio

from poll import Poll


class DiscordPoll(Poll):

    def __init__(self, item_list: list, headline: str, guild: discord.Guild, channel: discord.TextChannel, *, description: str = None, lifetime=None):
        super().__init__(item_list, headline)
        self.guild = guild
        self.description = description
        self.channel = channel
        self.message = None
        # lifetime will be stored in minutes
        self.lifetime = lifetime
        self.active = False

    async def add_item(self, item):
        if (self.lifetime > 0 or self.lifetime is None) and self.active:
            curr_highest_item = self.highest_item
            super().add_item(item)
            if self.highest_item != curr_highest_item:
                await self.message.edit(embed=get_poll_as_embed(self))

    async def remove_item(self, item):
        if (self.lifetime > 0 or self.lifetime is None) and self.active:
            curr_highest_item = self.highest_item
            super().remove_item(item)
            if self.highest_item != curr_highest_item:
                await self.message.edit(embed=get_poll_as_embed(self))

    def start(self, message):
        if self.lifetime != None:
            print("Started Poll")

        self.active = True
        self.message = message

    def end(self):
        # TODO read api description for this funciton again for error handling
        pass


def get_poll_as_embed(poll: DiscordPoll):
    embed = discord.Embed(title=poll.headline,
                          colour=discord.Colour.blue())

    if poll.description is not None:
        embed.description = poll.description
    for key in poll.item_list:
        embed.add_field(
            name='\u200b', value=f"{key}: {poll.item_list[key]}", inline=False)
    if poll.highest_item is not None and poll.active:
        embed.add_field(
            name='\u200b', value=f"**Meiste Stimmen**: {poll.item_list[poll.highest_item]}")

    embed.set_thumbnail(url=poll.guild.icon_url)

    if poll.active or poll.lifetime > 0:
        days_left = int((poll.lifetime / 60) / 24)
        hours_left = int(poll.lifetime / 60) - 24 * days_left
        minutes_left = int(poll.lifetime - days_left *
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
            text=f"Übrige Zeit: {days_left_string}T {hours_left_string}S {minutes_left_string}M")
    else:
        if poll.highest_item is not None:
            embed.add_field(
                name='\u200b', value=f"**Gewonnen hat**: {poll.item_list[poll.highest_item]}")
        else:
            embed.add_field(
                name='\u200b', value="Leider hat keiner bei der Umfrage mitgemacht uwu")

    return embed
