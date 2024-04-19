# Description: Add roles for a certain amount of reputation points

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from ..utils.database import reputation_roles

class ReputationRoles(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Add a role for a certain amount of reputation points
    @app_commands.command(name="role_add", description="Ajouter un rôle pour un certain nombre de points de réputation")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_add(self, interaction: discord.Interaction, selected_role: discord.Role, amount: int):
        
        await reputation_roles.insert_one({
            "role_id": selected_role.id,
            "amount": amount
        })

        await interaction.response.send_message(f"Le rôle {selected_role.mention} a été ajouté avec succès pour {amount} points de réputation", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReputationRoles(bot))