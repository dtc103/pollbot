from poll import Poll

import discord
from discord.ext import tasks, commands


class DiscordPoll(Poll):

    def __init__(self, item_list, headline: str,  channel: discord.TextChannel, message_id, guild, *, description: str = None, lifetime: int):
        super().__init__(item_list, headline)
        self.guild = guild
        self.description = description
        self.channel = channel
        self.id = message_id
        # lifetime will be stored in minutes
        self.lifetime = lifetime

    def add_item(self, item):
        if self.lifetime > 0:
            super().add_item(item)

    def remove_item(self, item):
        if self.lifetime > 0:
            super().remove_item(item)

    def start(self):
        self.lifetime_management.start()

    async def end(self):
        # TODO read api description for this funciton again for error handling
        self.lifetime_management.stop()
        print(str(self))

    @tasks.loop(seconds=1.0)
    async def lifetime_management(self):
        if self.lifetime <= 0:
            await self.end()

        self.lifetime -= 1
