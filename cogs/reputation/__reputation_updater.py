# Description: Updates the role of the player based on the reputation points and database role

from os import remove
import discord
from discord.ext import commands

from ..utils import colorEmbed
from ..utils.database import reputation_members, reputation_roles, reputation_channels

async def update_reputation_role(guild, member, action):
    # * Fetch reputation points of the member from the database
    reputation_data = await reputation_members.find_one({"_guildID": guild.id, "_memberID": member.id})
    reputation_channels_data = await reputation_channels.find_one({"_guildID": guild.id})

    if reputation_data is None:
        return

    reputation_points = reputation_data["_reputationPoints"]

    # * Fetch reputation roles from the database
    roles_data = await reputation_roles.find({"_guildID": guild.id}).to_list(length=None)

    # * Sort roles by reputation points in descending order
    roles_data.sort(key=lambda x: x["_reputationPoints"], reverse=True)

    # * Get current roles of the member
    current_roles = [role.id for role in member.roles]

    # * Extract role IDs from the reputation_roles database
    reputation_role_ids = {role["_roleID"] for role in roles_data}

    # * Keep track of the highest role that the member qualifies for
    highest_role_id = None

    # * Find the highest role the member qualifies for
    for role_data in roles_data:
        role_id = role_data["_roleID"]
        reputation_points_required = role_data["_reputationPoints"]

        if reputation_points >= reputation_points_required:
            highest_role_id = role_id
            break

    # * Filter out the roles not related to the reputation_roles database
    filtered_roles = [role_id for role_id in current_roles if role_id in reputation_role_ids]

    # * If member already has the highest role, do nothing
    if highest_role_id in filtered_roles:
        return None

    # * Remove all filtered roles from the member
    await member.remove_roles(*[guild.get_role(role_id) for role_id in filtered_roles])

    # * Add the highest role the member qualifies for
    if highest_role_id:
        role = guild.get_role(highest_role_id)
        if role:
            await member.add_roles(role)
            FelicitationEmbed = discord.Embed(description=f"Félicitations à {member.mention}, il a obtenu le rôle {role.mention}!", color=colorEmbed.Purple).set_author(name= member.display_name, icon_url= member.display_avatar)
            if reputation_channels_data is None:
                return

            channel = guild.get_channel(reputation_channels_data["_channelID"])
            if channel is None:
                return
            if action == "add":
                await channel.send(embed=FelicitationEmbed)
            elif action == "remove":
                removedRole = guild.get_role(filtered_roles[0])
                RemoveEmbed = discord.Embed(description=f"{member.mention} a perdu sont role {removedRole.mention} et a reçu le role {role.mention}!", color=colorEmbed.Purple).set_author(name= member.display_name, icon_url= member.display_avatar)
                await channel.send(embed=RemoveEmbed)

    # Return the roles added and removed for logging or further processing
    return highest_role_id