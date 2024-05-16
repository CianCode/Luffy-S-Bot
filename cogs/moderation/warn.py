# Description: Warn system for the bot

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from ..utils import colorEmbed
from ..utils.database import warn_members

class WarnViewDelete(discord.ui.View):
    def __init__(self, bot, options, max):
        super().__init__(placeholder='Select a warn!', options=options, min_values=1, max_values=max)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # * Create the embeds
        SuccesEmbed = discord.Embed(description="The warns have been removed", color=colorEmbed.Green)

        # * Get the selected warns
        selected_warns = interaction.data['values']

        # * Remove the selected warns
        for warn in selected_warns:
            await warn_members.delete_one({"_id": int(warn)})

        # * Create the embed
        SuccesEmbed = discord.Embed(description="The warns have been removed", color=colorEmbed.Green)
        await interaction.response.send_message(embed=SuccesEmbed, ephemeral=False)

class WarnSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warn a member")
    @commands.has_permissions(manage_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        # * Create the embeds
        ErrorEmbed = discord.Embed(description="You can't warn yourself or a bot!", color=colorEmbed.Red)
        SuccesEmbed = discord.Embed(description=f"{member.mention} has been warned for {reason}", color=colorEmbed.Green)

        # * Check if the member is the bot
        if member == interaction.guild.me:
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return

        # * Add the warn
        await warn_members.insert_one({"_guildID": interaction.guild_id, "_memberID": member.id, "_reason": reason})
        await interaction.response.send_message(embed=SuccesEmbed, ephemeral=False)

    @app_commands.command(name="warns_remove", description="Remove members warns")
    @commands.has_permissions(manage_members=True)
    async def warns_remove(self, interaction: discord.Interaction, member: discord.Member):
        # * Create the embeds
        AskEmbed = discord.Embed(description=f"Wich warn from {member.mention} do you want to delete?", color=colorEmbed.Purple)
        ErrorEmbed = discord.Embed(description=f"{member.mention} has no warns!", color=colorEmbed.Red)

        # * Check if the member has any warns
        if not await warn_members.find_one({"_guildID": interaction.guild_id, "_memberID": member.id}):
            await interaction.response.send_message(embed=ErrorEmbed, ephemeral=True)
            return
        
        # * Create the options with all the warns of a member
        options = [
            discord.SelectOption(label=f"{warn['_reason']}", value=f"{warn['_id']}")
            for warn in await warn_members.find({"_guildID": interaction.guild_id, "_memberID": member.id}).to_list(length=None)
        ]

        # * Create the view
        view = WarnViewDelete(self.bot, options, len(options))
        await interaction.response.send_message(embed=AskEmbed, view=view, ephemeral=True)
        


# * Setup the warn command
async def setup(bot):
    await bot.add_cog(WarnSystem(bot))
