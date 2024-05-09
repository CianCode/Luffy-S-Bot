# Description: This file contains the code to store the warns of the members.

# * Import discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from ..utils.database import warns, reputation_members
from ..utils import colorEmbed
from ..reputation.__reputation_updater import update_reputation_role

class Warns(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Add a warn to a member
    @app_commands.command(name="warn_add", description="Ajouter un avertissement à un membre")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn_add(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        
        # * Create the embed
        WarnAddedEmbed = discord.Embed(description=f"{member.mention} a été warn pour la reason suivante: \n **{reason}**", color=colorEmbed.Purple).set_author(name=interaction.user, icon_url=interaction.user.display_avatar)
        
        # * Check if guild exists
        if not interaction.guild:
            return
        
        # * Add the warn to the member with a id that calculates the number of warns
        await warns.insert_one({
            "_guildID": interaction.guild.id,
            "_memberID": member.id,
            "_warnID": await warns.count_documents({"_guildID": interaction.guild.id, "_memberID": member.id}) + 1,
            "_reason": reason
        })

        # * Remove 20 reputation points from the member
        reputationMember = await reputation_members.find_one({
            "_guildID": interaction.guild.id,
            "_memberID": member.id
        })

        if reputationMember:
            await reputation_members.update_one({
                "_guildID": interaction.guild.id,
                "_memberID": member.id
            }, {
                "$set": {
                    "_reputationPoints": reputationMember["_reputationPoints"] - 20
                }
            })
        
            await interaction.response.send_message(embed=WarnAddedEmbed, ephemeral=False)
            await update_reputation_role(interaction.guild, member, "remove")

    # * Remove a warn to a member
    @app_commands.command(name="warn_remove", description="Retirer un avertissement à un membre")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn_remove(self, interaction: discord.Interaction, member: discord.Member, id: int):
        
        # * Create the embed
        WarnRemovedEmbed = discord.Embed(description=f"{member.mention} a été unwarn!", color=colorEmbed.Blue)
        WarnErrorNoneEmbed = discord.Embed(description=f"{member.mention} n'a pas d'avertissement avec l'ID: {id}!", color=colorEmbed.Red)

        # * Check if guild exists
        if not interaction.guild:
            return
        
        # * Check if the member has a warn
        warn = await warns.find_one({
            "_guildID": interaction.guild.id,
            "_memberID": member.id,
            "_warnID": id
        })
        
        if not warn:
            return await interaction.response.send_message(embed=WarnErrorNoneEmbed, ephemeral=True)
        
        # * Remove the warn from the member
        await warns.delete_one({
            "_guildID": interaction.guild.id,
            "_memberID": member.id,
            "_warnID": id
        })
        
        await interaction.response.send_message(embed=WarnRemovedEmbed, ephemeral=False)

    # * Get the warns of a member
    @app_commands.command(name="warns", description="Obtenir les avertissements d'un membre")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warns(self, interaction: discord.Interaction, member: discord.Member):
        
        # * Create the embed
        WarnsEmbed = discord.Embed(title=f"Avertissements de {member}", color=colorEmbed.Yellow)
        WarnsErrorNoneEmbed = discord.Embed(description=f"{member.mention} n'a pas d'avertissement!", color=colorEmbed.Red)
        
        # * Check if guild exists
        if not interaction.guild:
            return
        
        # * Get the warns of the member
        warnsMember = await warns.find({"_guildID": interaction.guild.id, "_memberID": member.id}).to_list(length=None)

        if not warnsMember:
            return await interaction.response.send_message(embed=WarnsErrorNoneEmbed, ephemeral=True)

        # * Add the warns to the embed
        for warn in warnsMember:
            WarnsEmbed.add_field(name=f"ID: {warn['_warnID']}", value=f"Raison: {warn['_reason']}", inline=False)
        
        await interaction.response.send_message(embed=WarnsEmbed, ephemeral=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Warns(bot))