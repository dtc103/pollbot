from poll import Poll

import discord
from discord.ext import tasks, commands

class DiscordPoll(Poll):
                    
    def __init__(self, item_list, headline:str,  channel: discord.TextChannel, message_id, *, description:str=None, lifetime:int):
        super().__init__(item_list, headline)
        self.description = description
        self.channel = channel
        self.id = message_id
        #lifetime will be stored in minutes
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
        #TODO read api description for this funciton again for error handling
        self.lifetime_management.stop()
        print(str(self))

    def get_as_embed(self):
        embed = discord.Embed(title=self.headline,
                              colour=discord.Colour.blue())
        if self.description is not None:
            embed.description = self.description
        for key in self.item_list:
            embed.add_field(
                name='\u200b', value=f"{key}: {self.item_list[key]}", inline=False)
        if self.highest_item is not None:
            embed.add_field(
                name='\u200b', value=f"**Most votes**: {self.item_list[self.highest_item]}")

        embed.set_thumbnail(url=self.channel.guild.icon_url)

        days_left = int((self.lifetime / 60) / 24)
        hours_left = int(self.lifetime / 60) - 24 * days_left
        minutes_left = int(self.lifetime - days_left * 24 * 60 - hours_left * 60)

        embed.set_footer(text=f"Time left: {days_left}:{hours_left}:{minutes_left}")

        return embed

    @tasks.loop(seconds=1.0)
    async def lifetime_management(self):
        if self.lifetime <= 0:
            await self.end()

        self.lifetime -= 1
        


