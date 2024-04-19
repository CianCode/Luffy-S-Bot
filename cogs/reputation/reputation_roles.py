# Description: Add roles for a certain amount of reputation points

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from ..utils.database import reputation_roles
from ..utils import colorEmbed

class ReputationRoles(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Add a role for a certain amount of reputation points
    @app_commands.command(name="role_add", description="Ajouter un rôle pour un certain nombre de points de réputation")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_add(self, interaction: discord.Interaction, selected_role: discord.Role, amount: int):

        # * Create the embeds
        ErrorEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} existe déja! Supprimer le pour modifier la quantité", color=colorEmbed.Red)
        SuccesEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} a été ajouté pour {amount} points de réputation", color=colorEmbed.Green)
        
        # * Check if the role already exists
        if await reputation_roles.find_one({"_roleID": selected_role.id}):
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return

        # * Add the role
        await reputation_roles.insert_one({"_roleID": selected_role.id, "_reputationPoints": amount})
        await interaction.response.send_message(embed=SuccesEmbed, ephemeral=False)

    # * Remove a role from the database
    @app_commands.command(name="role_remove", description="Supprimer un rôle pour un certain nombre de points de réputation")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_remove(self, interaction: discord.Interaction, selected_role: discord.Role):

        # * Create the embeds
        ErrorEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} n'existe pas!", color=colorEmbed.Red)
        SuccesEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} a été supprimé", color=colorEmbed.Green)

        # * Check if the role exists
        if not await reputation_roles.find_one({"_roleID": selected_role.id}):
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return

        # * Remove the role
        await reputation_roles.delete_one({"_roleID": selected_role.id})
        await interaction.response.send_message(embed=SuccesEmbed, ephemeral=False)

    # * List all the roles in the database
    @app_commands.command(name="role_list", description="Lister tous les rôles pour un certain nombre de points de réputation")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_list(self, interaction: discord.Interaction):
        
        # * Create the embed
        ErrorEmbed = discord.Embed(description=f"Il n'y a aucun rôle dans la database!", color=colorEmbed.Red)
        ShowEmbed = discord.Embed(title="Liste des rôles de réputation", color=colorEmbed.Purple)
        
        # * Check if the role exists
        if not await reputation_roles.find_one({"_roleID": {"$exists": True}}):
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return

        # * Get all the roles
        roles = await reputation_roles.find({}).to_list(length=None)

        # * Sort roles by reputation points (high to low)
        sorted_roles = sorted(roles, key=lambda x: x['_reputationPoints'], reverse=True)

        # * Add the roles to the embed
        for role in sorted_roles:
            roleID = role["_roleID"]
            reputationPoints = role["_reputationPoints"]
            role = interaction.guild.get_role(roleID) # type: ignore
            ShowEmbed.add_field(name=role.name, value=f"Points de réputation: {reputationPoints}", inline=False) # type: ignore

        await interaction.response.send_message(embed=ShowEmbed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(ReputationRoles(bot))