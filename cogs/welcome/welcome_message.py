# Description: This file is used to send a canvas to a channel when a member joins the server.

# * Import the necessary libraries
import discord
from discord.ext import commands

from ..utils import colorEmbed
from ..utils.database import welcome_channels

# * Create the WelcomeMessage class
class WelcomeMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Event to send the welcome message when a member joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):

        # * Create the embed
        Embed = discord.Embed(
            description=f"Bienvenue {member.mention} monte à bord avec nous vèrs l'aventure!",
            color=colorEmbed.generate_random_color()
        ).set_author(
            name=member.guild.name,
            icon_url=member.guild.icon.url
        ).set_footer(
            text=f"ID: {member.id}",
            icon_url=member.display_avatar
        )

        # * Get the welcome channel
        channel_data = await welcome_channels.find_one({"_guildID": member.guild.id})
        if channel_data is not None:
            channel = member.guild.get_channel(channel_data["_channelID"])
        else:
            channel = None

        # * Send the welcome message
        if channel is not None:
            await channel.send(embed=Embed)


# * Setup the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeMessage(bot))