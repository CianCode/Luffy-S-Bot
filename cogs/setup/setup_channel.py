# Description: setup channel commands

# * Import the necessary libraries
import discord
from discord import app_commands
from discord.ext import commands

from ..utils import colorEmbed
from ..utils.database import reputation_channels, welcome_channels

class SetupChannel(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # * Setup the felicitation channel
    @app_commands.command(name="setup_felicitation", description="Configurer le salon")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_felicitation(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # * Create the embeds
        CreateChannelEmbed = discord.Embed(description=f"Le salon pour les félicitation a été configuré dans le channel {channel.mention}!", color=colorEmbed.Green)
        ModifyChannelEmbed = discord.Embed(description=f"Le salon pour les félicitation a été modifié dans le channel {channel.mention}!", color=colorEmbed.Yellow)

        if await reputation_channels.find_one({"_guildID": interaction.guild_id}):
            await reputation_channels.update_one({"_guildID": interaction.guild_id}, {"$set": {"_channelID": channel.id}})
            await interaction.response.send_message(embed=ModifyChannelEmbed, ephemeral=True)

        else:
            await reputation_channels.insert_one({"_guildID": interaction.guild_id, "_channelID": channel.id})
            await interaction.response.send_message(embed=CreateChannelEmbed, ephemeral=True)

    # * Setup the welcome channel
    @app_commands.command(name="setup_welcome", description="Configurer le salon")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # * Create the embeds
        CreateChannelEmbed = discord.Embed(description=f"Le salon pour les bienvenue a été configuré dans le channel {channel.mention}!", color=colorEmbed.Green)
        ModifyChannelEmbed = discord.Embed(description=f"Le salon pour les bienvenue a été modifié dans le channel {channel.mention}!", color=colorEmbed.Yellow)

        if await welcome_channels.find_one({"_guildID": interaction.guild_id}):
            await welcome_channels.update_one({"_guildID": interaction.guild_id}, {"$set": {"_channelID": channel.id}})
            await interaction.response.send_message(embed=ModifyChannelEmbed, ephemeral=True)

        else:
            await welcome_channels.insert_one({"_guildID": interaction.guild_id, "_channelID": channel.id})
            await interaction.response.send_message(embed=CreateChannelEmbed, ephemeral=True)


# * Setup the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(SetupChannel(bot))