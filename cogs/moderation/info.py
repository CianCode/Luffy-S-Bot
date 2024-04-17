# * Import the necessary discord libraries
import discord
from discord.ext import commands

class InfoBot(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # TODO: Add the info command to get the bot information (Slash Commands or Hybrid Commands)


async def setup(bot):
    await bot.add_cog(InfoBot(bot))