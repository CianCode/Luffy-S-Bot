# Description: Warn system for the bot

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from bson import ObjectId
from ..utils import colorEmbed
from ..utils.database import warn_members

class WarnViewDelete(discord.ui.Select):
    def __init__(self, bot, options, max):
        super().__init__(placeholder='Selectionner un warn!', options=options, min_values=1, max_values=max)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # Create the embed
        SuccessEmbed = discord.Embed(description="Le warn a été supprimer", color=colorEmbed.Green)

        # Get the selected warns
        selected_warns = interaction.data['values']

        # Remove the selected warns
        for warn in selected_warns:
            await warn_members.delete_one({"_id": ObjectId(warn)})

        await interaction.response.send_message(embed=SuccessEmbed, ephemeral=False)

class WarnSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warn a member")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        # * Create the embeds
        ErrorEmbed = discord.Embed(description="Tu ne peux pas te warn toi même ou un bot!", color=colorEmbed.Red)
        SuccessEmbed = discord.Embed(description=f"{member.mention} a été warn pour la raison suivante > {reason}", color=colorEmbed.Green)

        # * Check if the member is the bot
        if member.id == interaction.user.id or member.bot:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return
        
        # * Get the time of the warn and the date of the warn (The time need to have only the date, hours and minutes)
        time = interaction.created_at
        time = time.strftime("%d/%m/%Y - %H:%M")

        # * Add the warn
        await warn_members.insert_one({"_guildID": interaction.guild_id, "_memberID": member.id, "_reason": reason, "_time": time})
        await interaction.response.send_message(embed=SuccessEmbed, ephemeral=False)

    @app_commands.command(name="warns_remove", description="Supprime un warn d'un membre")
    @commands.has_permissions(moderate_members=True)
    async def warns_remove(self, interaction: discord.Interaction, member: discord.Member):
        # * Create the embeds
        AskEmbed = discord.Embed(description=f"Quelles sont les warn de {member.mention} voullez vous supprimer ?", color=colorEmbed.Purple)
        ErrorEmbed = discord.Embed(description=f"{member.mention} ne possède pas de warn. Quelle membre exemplaire!", color=colorEmbed.Red)

        # * Check if the member has any warns
        if not await warn_members.find_one({"_guildID": interaction.guild_id, "_memberID": member.id}):
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return
        
        # * Create the options with all the warns of a member
        options = [
            discord.SelectOption(label=f"{warn['_reason']}", value=f"{warn['_id']}", description=f"Date / Heure du warn: {warn['_time']}")
            for warn in await warn_members.find({"_guildID": interaction.guild_id, "_memberID": member.id}).to_list(length=None)
        ]

        # * Create the view
        select = WarnViewDelete(self.bot, options, len(options))
        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message(embed=AskEmbed, view=view, ephemeral=True)

    # * Affiche tout les warn du membre mentionné
    @app_commands.command(name="warns_list", description="Liste tout les warn d'un membre")
    @commands.has_permissions(moderate_members=True)
    async def warns_list(self, interaction: discord.Interaction, member: discord.Member):
        # * Create the embeds
        ErrorEmbed = discord.Embed(description=f"{member.mention} ne possède pas de warn. Quelle membre exemplaire!", color=colorEmbed.Red)
        ListEmbed = discord.Embed(title=f"Liste des warn de {member.display_name}", color=colorEmbed.Purple)

        # * Get the warns
        warns = await warn_members.find({"_guildID": interaction.guild_id, "_memberID": member.id}).to_list(length=None)

        # * Check if the member has any warns
        if not warns:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return

        # * Add the warns to the embed
        for warn in warns:
            ListEmbed.add_field(name=f"Date / Heure du warn: {warn['_time']}", value=f"Raison: {warn['_reason']}", inline=False)

        await interaction.response.send_message(embed=ListEmbed, ephemeral=True)

        


# * Setup the warn command
async def setup(bot):
    await bot.add_cog(WarnSystem(bot))
