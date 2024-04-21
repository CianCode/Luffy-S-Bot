# Description: Add reputation points to a member

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from ..utils.database import reputation_members
from ..utils import colorEmbed

from .__reputation_updater import update_reputation_role

class ReputationMembers(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Add reputation points to a member
    @app_commands.command(name="reputation_add", description="Ajouter des points de réputation à un membre")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reputation_add(self, interaction: discord.Interaction, selected_member: discord.Member, amount: int):

        # * Create the embeds
        CreateMembersEmbed = discord.Embed(description=f"{selected_member.mention} a été ajouter et a maintenant {amount} points de réputation", color=colorEmbed.Green)
        AddReputationEmbed = discord.Embed(description=f"Vous venez d'ajouter {amount} points de réputation à {selected_member.mention}", color=colorEmbed.Green)
        
        # * Check if the member already exists
        if await reputation_members.find_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id}) is None:
            await reputation_members.insert_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id, "_reputationPoints": amount})
            await update_reputation_role(interaction.guild, selected_member)
            await interaction.response.send_message(embed=CreateMembersEmbed, ephemeral=False)
            return
        
        # * Add the reputation points
        reputation = await reputation_members.find_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id})
        quantity = reputation["_reputationPoints"] # type: ignore
        quantity += amount
        await reputation_members.replace_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id}, {"_guildID": interaction.guild_id, "_memberID": selected_member.id, "_reputationPoints": quantity})
        await update_reputation_role(interaction.guild, selected_member)
        await interaction.response.send_message(embed=AddReputationEmbed, ephemeral=False)

    # * Remove reputation points from a member
    @app_commands.command(name="reputation_remove", description="Supprimer des points de réputation à un membre")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reputation_remove(self, interaction: discord.Interaction, selected_member: discord.Member, amount: int):

        # * Create the embeds
        ErrorEmbed = discord.Embed(description=f"{selected_member.mention} n'existe pas!", color=colorEmbed.Red)
        RemoveReputationEmbed = discord.Embed(description=f"Vous venez de supprimer {amount} points de réputation à {selected_member.mention}", color=colorEmbed.Green)
        
        # * Check if the member exists
        if await reputation_members.find_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id}) is None:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return
        
        # * Remove the reputation points
        reputation = await reputation_members.find_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id})
        quantity = reputation["_reputationPoints"] # type: ignore
        quantity -= amount
        await reputation_members.replace_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id}, {"_guildID": interaction.guild_id, "_memberID": selected_member.id, "_reputationPoints": quantity})
        highestRole = await update_reputation_role(interaction.guild, selected_member)
        await interaction.response.send_message(embed=RemoveReputationEmbed, ephemeral=False)

    # * Show the reputation points of a member (default is the author)
    @app_commands.command(name="reputation_show", description="Afficher les points de réputation d'un membre")
    async def reputation_show(self, interaction: discord.Interaction, selected_member: discord.Member):
        
        # * Create the embed
        ErrorEmbed = discord.Embed(description=f"{selected_member.mention} ne possède pas de point!", color=colorEmbed.Red)

        # * Check if the member exists
        if await reputation_members.find_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id}) is None:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return
        
        # * Show the reputation points
        reputation = await reputation_members.find_one({"_guildID": interaction.guild_id, "_memberID": selected_member.id})
        if reputation is not None:
            # * Create the embed
            ShowReputationEmbed = discord.Embed(description=f"{selected_member.mention} a {reputation['_reputationPoints']} points de réputation", color=colorEmbed.Yellow)
            await interaction.response.send_message(embed=ShowReputationEmbed, ephemeral=False)
    
    # * Leaderboard of the members with the most reputation points
    @app_commands.command(name="reputation_leaderboard", description="Afficher le classement des membres avec le plus de points de réputation")
    async def reputation_leaderboard(self, interaction: discord.Interaction):
        
        # * Create the embed
        ErrorEmbed = discord.Embed(description="Il n'y a aucun membre pour le moment", color=colorEmbed.Red)

        # * Get the members
        members = await reputation_members.find({"_guildID": interaction.guild_id}).to_list(length=None)

        # * Check if there are no members
        if not members:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return

        # * Sort the members by reputation points
        members = sorted(members, key=lambda member: member["_reputationPoints"], reverse=True)

        # * Create the embed
        LeaderboardEmbed = discord.Embed(title="Classement des membres avec le plus de points de réputation", color=colorEmbed.Yellow)
        for i, member in enumerate(members):
            member_id = member["_memberID"]
            reputation_points = member["_reputationPoints"]
            member = interaction.guild.get_member(member_id) # type: ignore
            if member:
                LeaderboardEmbed.add_field(name=f"{i+1}. {member.display_name}", value=f"Points de réputation: {reputation_points}", inline=False)
        
        await interaction.response.send_message(embed=LeaderboardEmbed, ephemeral=False)
        

async def setup(bot):
    await bot.add_cog(ReputationMembers(bot))