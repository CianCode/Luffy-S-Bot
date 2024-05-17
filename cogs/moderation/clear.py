# Description: Efface un nombre de messages !

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from ..utils import colorEmbed


class Clear(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.checks.has_permissions(manage_messages=True)
    @commands.guild_only()
    @app_commands.command(name="clear", description="Efface un nombre de messages !")
    async def clear(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        pass

async def setup(bot):
    await bot.add_cog(Clear(bot))