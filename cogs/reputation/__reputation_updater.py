# Description: Updates the role of the player based on the reputation points and database role

import discord
from discord.ext import commands

from ..utils.database import reputation_members, reputation_roles

async def update_reputation_role(guild, member):
    # * Fetch reputation points of the member from the database
    reputation_data = await reputation_members.find_one({"_guildID": guild.id, "_memberID": member.id})

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

    # * Remove all filtered roles from the member
    await member.remove_roles(*[guild.get_role(role_id) for role_id in filtered_roles])

    # * Add the highest role the member qualifies for
    if highest_role_id:
        role = guild.get_role(highest_role_id)
        if role:
            await member.add_roles(role)

    # Return the roles added and removed for logging or further processing
    return highest_role_id