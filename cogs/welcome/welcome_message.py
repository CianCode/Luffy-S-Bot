# Description: This file is used to send a canvas to a channel when a member joins the server.

# * Import the necessary libraries
import discord
from discord import File
from discord.ext import commands
from discord import app_commands

import aiohttp
from io import BytesIO

from easy_pil import Editor, load_image_async, Font

from ..utils import colorEmbed
from ..utils.database import welcome_channels, welcome_banner

# * Create the WelcomeMessage class
class WelcomeMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Setup the background image
    @app_commands.command(name="welcome_banner", description="Configurer le background")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_banner(self, interaction: discord.Interaction, url: str):
        # * Create the embeds
        CreateChannelEmbed = discord.Embed(description=f"Le background pour les bienvenue a été configuré!", color=colorEmbed.Green)
        ModifyChannelEmbed = discord.Embed(description=f"Le background pour les bienvenue a été modifié!", color=colorEmbed.Yellow)

        if await welcome_banner.find_one({"_guildID": interaction.guild_id}):
            await welcome_banner.update_one({"_guildID": interaction.guild_id}, {"$set": {"_backgroundURL": url}})
            await interaction.response.send_message(embed=ModifyChannelEmbed, ephemeral=True)

        else:
            await welcome_banner.insert_one({"_guildID": interaction.guild_id, "_backgroundURL": url})
            await interaction.response.send_message(embed=CreateChannelEmbed, ephemeral=True)

    # * Setup welcome texte
    @app_commands.command(name="welcome_texte", description="Configurer le texte de bienvenue")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_texte(self, interaction: discord.Interaction, texte: str):
        # * Create the embeds
        CreateChannelEmbed = discord.Embed(description=f"Le texte de bienvenue a été configuré!", color=colorEmbed.Green)
        ModifyChannelEmbed = discord.Embed(description=f"Le texte de bienvenue a été modifié!", color=colorEmbed.Yellow)

        if await welcome_banner.find_one({"_guildID": interaction.guild_id}):
            await welcome_banner.update_one({"_guildID": interaction.guild_id}, {"$set": {"_texte": texte}})
            await interaction.response.send_message(embed=ModifyChannelEmbed, ephemeral=True)

        else:
            await welcome_banner.insert_one({"_guildID": interaction.guild_id, "_texte": texte})
            await interaction.response.send_message(embed=CreateChannelEmbed, ephemeral=True)

    # * Event to send the welcome message when a member joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):

        # * Retrieve the background image
        background_data = await welcome_banner.find_one({"_guildID": member.guild.id})
        background_url = background_data["_backgroundURL"] if background_data else "https://cdn.discordapp.com/attachments/1231627775576772732/1231701536359583834/pic1.jpg?ex=6637ea72&is=66257572&hm=a4b5f76be7ee166b5bf003062b7ea729ef1b6ab2838730e4d98e3849ea3e7f8c&"

        # Download the image from the URL
        async with aiohttp.ClientSession() as session:
            async with session.get(background_url) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                else:
                    print(f"Failed to download image. Status code: {response.status}")
                    return
                
        # * Create the canvas
        background = Editor(BytesIO(image_bytes))
        profile_image = await load_image_async(str(member.display_avatar.url))

        profile = Editor(profile_image).resize((150, 150)).circle_image()
        poppins = Font.poppins(size=50, variant="bold")

        poppins_small = Font.poppins(size=20, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

        background.text((400, 260), f"BIENVENUE TO {member.guild.name}!", font=poppins, color="white", align="center")
        background.text((400, 325), f"{member.name}", font=poppins_small, color="white", align="center")

        file = File(fp=background.image_bytes, filename="welcome.png")

        # * Retrieve the welcome channel
        welcome_channel_data = await welcome_channels.find_one({"_guildID": member.guild.id})
        welcome_channel = member.guild.get_channel(welcome_channel_data["_channelID"]) if welcome_channel_data else None
        
        # * Send the welcome message if the welcome channel exists
        if welcome_channel:
            await welcome_channel.send(file=file)

# * Setup the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeMessage(bot))