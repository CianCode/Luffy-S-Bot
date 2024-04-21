# Description: This file is used to store roles id for the on_member_join event.

# * Import the necessary libraries
from uu import Error
import discord
from discord.ext import commands
from discord import app_commands

from ..utils.database import on_member_join_roles
from ..utils import colorEmbed

class MemberJoinRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Add roles to database
    @app_commands.command(name="add_roles_members", description="Ajouter des rôles à un membre lorsqu'il rejoint le serveur")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_roles_members(self, interaction: discord.Interaction, selected_role: discord.Role):
        # * Create the embeds
        AddRolesEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} a été ajouté à la liste des rôles pour les nouveaux membres", color=colorEmbed.Green)
        ErrorEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} est déjà dans la liste des rôles pour les nouveaux membres", color=colorEmbed.Red)

        # * Check if the role already exists
        if await on_member_join_roles.find_one({"_guildID": interaction.guild_id, "_roleID": selected_role.id}) is None:
            await on_member_join_roles.insert_one({"_guildID": interaction.guild_id, "_roleID": selected_role.id})
            await interaction.response.send_message(embed=AddRolesEmbed, ephemeral=False)
            return

        await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)

    # * Remove roles from database
    @app_commands.command(name="remove_roles_members", description="Supprimer des rôles à un membre lorsqu'il rejoint le serveur")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_roles_members(self, interaction: discord.Interaction, selected_role: discord.Role):
        # * Create the embeds
        ErrorEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} n'est pas dans la liste des rôles pour les nouveaux membres", color=colorEmbed.Red)
        RemoveRolesEmbed = discord.Embed(description=f"Le rôle {selected_role.mention} a été supprimé de la liste des rôles pour les nouveaux membres", color=colorEmbed.Green)

        # * Check if the role exists
        if await on_member_join_roles.find_one({"_guildID": interaction.guild_id, "_roleID": selected_role.id}) is None:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return

        await on_member_join_roles.delete_one({"_guildID": interaction.guild_id, "_roleID": selected_role.id})
        await interaction.response.send_message(embed=RemoveRolesEmbed, ephemeral=False)

    # * List roles for new members
    @app_commands.command(name="list_roles_members", description="Liste des rôles pour les nouveaux membres")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_roles_members(self, interaction: discord.Interaction):
        # *Create the embed
        ListRolesEmbed = discord.Embed(title="Liste des rôles pour les nouveaux membres", color=colorEmbed.Pink)
        ErrorEmbed = discord.Embed(description="Il n'y a pas de rôles pour les nouveaux membres", color=colorEmbed.Red)
        
        if interaction.guild is not None:
            roles = interaction.guild.roles
        else:
            roles = []

        # * Filter out roles that are not in the database
        roles_data = await on_member_join_roles.find({"_guildID": interaction.guild_id}).to_list(None)
        role_ids = [role_data["_roleID"] for role_data in roles_data]

        # * Sort roles by position in the role hierarchy in reverse order
        roles = sorted(roles, key=lambda x: x.position, reverse=True)
        roles = [role for role in roles if role.id in role_ids]

        # * Check if there are roles
        if len(roles) == 0:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=False)
            return

        # * Add the roles to the embed with spaces between them
        role_mentions = "\n\n".join([role.mention for role in roles])
        ListRolesEmbed.description = role_mentions

        await interaction.response.send_message(embed=ListRolesEmbed, ephemeral=False)


    # * Add the roles to new members
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # * Get the roles from the database
        roles = await on_member_join_roles.find({"_guildID": member.guild.id}).to_list(None)

        # * Add the roles to the new member
        for role in roles:
            role_id = role["_roleID"]
            role = member.guild.get_role(role_id)
            if role is not None:
                await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(MemberJoinRoles(bot))
