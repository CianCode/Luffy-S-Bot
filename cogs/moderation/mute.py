# Description: Mute command to mute a member

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
import asyncio
from ..utils import colorEmbed

class Mute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Mute a member
    @app_commands.command(name="mute", description="Mute un membre")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str, time: int):
        
        # * Create the embeds
        ErrorEmbed = discord.Embed(description="Vous ne pouvez pas vous mute vous même", color=colorEmbed.Red)
        ErrorRoleEmbed = discord.Embed(description="Le rôle Mute n'existe pas!", color=colorEmbed.Red)
        SuccesEmbed = discord.Embed(description=f"{member.mention} a été mute pour la raison suivante: {reason} pendant {time} secondes", color=colorEmbed.Green)
        SuccesDemuteEmbed = discord.Embed(description=f"{member.mention} a été demute", color=colorEmbed.Green)
        
        # * Check if the member is the author
        if member.id == interaction.user.id or member.bot:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return
        
        # * Mute the member with a role named Mute for the specified time
        if interaction.guild is not None:
            role = discord.utils.get(interaction.guild.roles, name="Mute")
            if role is not None:
                await member.add_roles(role)
                await interaction.response.send_message(embed=SuccesEmbed, ephemeral=False)
                await asyncio.sleep(time)
                await member.remove_roles(role)
            else:
                await interaction.response.send_message(embed=ErrorRoleEmbed, ephemeral=True)
                return
    
    # * Unmute a member
    @app_commands.command(name="unmute", description="Unmute un membre")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        
        # * Create the embeds
        SuccesEmbed = discord.Embed(description=f"{member.mention} a été demute", color=colorEmbed.Green)
        NotMuteEmbed = discord.Embed(description=f"{member.mention} n'est pas mute", color=colorEmbed.Red)
        
        # * Unmute the member
        if interaction.guild is not None:
            role = discord.utils.get(interaction.guild.roles, name="Mute")
            # * Check if the member has the role Mute
            if role in member.roles:
                await member.remove_roles(role)
                await interaction.response.send_message(embed=SuccesEmbed, ephemeral=False)
            else:
                await interaction.response.send_message(embed=NotMuteEmbed, ephemeral=True)
                return


# * Setup the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Mute(bot))
