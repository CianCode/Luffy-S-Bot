# * Import the necessary discord libraries
import discord
from discord.ext import commands

class ReputationRoles(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # TODO: Add the reputation roles command to add role to the database


async def setup(bot):
    await bot.add_cog(ReputationRoles(bot))