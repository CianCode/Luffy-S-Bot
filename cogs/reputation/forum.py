# Description: Create the forum for help people questions

# * Import the necessary discord libraries
import discord
from discord import app_commands
from discord.ext import commands

# * Import the necessary libraries
from ..utils import colorEmbed
from ..utils.database import reputation_forum

progress = discord.ForumTag(name="En cours", emoji="🔨", moderated=False)
impossible = discord.ForumTag(name="Sans suite", emoji="🍂", moderated=False)
resolve = discord.ForumTag(name="Résolu", emoji="✅", moderated=False)

class Forum(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # * Create the forum for help people questions
    @app_commands.command(name="forum", description="Créer un forum pour les questions d'aide")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def forum(self, interaction: discord.Interaction, categorie: discord.CategoryChannel, channel_name: str, topic_name: str):

        # * Create the embed
        ForumCreatedEmbed = discord.Embed(description="Le forum a été créé avec succès!", color=colorEmbed.Green)
        ErrorNameEmbed = discord.Embed(description="Le nom du canal ne peut être que en minuscule et sans espace et a don été modifier pour suivre les règlementations !", color=colorEmbed.Red)

        # * Check if guild exists
        if not interaction.guild:
            return

        # * Check if the channel name is valid
        if " " in channel_name or channel_name.isupper():
            channel_name = channel_name.replace(" ", "-").lower()
        
        # * Create the forum
        if categorie:
            forum = await interaction.guild.create_forum(
                name=channel_name,
                topic=topic_name,
                category=categorie,
                position=0, nsfw=False, slowmode_delay=0, 
                reason="Forum Creation", 
                default_auto_archive_duration=10080, 
                default_thread_slowmode_delay=0, 
                default_sort_order=discord.ForumOrderType.latest_activity, 
                default_reaction_emoji="🔨",
                default_layout=discord.ForumLayoutType.list_view,  
                available_tags=[progress, impossible, resolve]
            )
            
            await interaction.response.send_message(embed=ForumCreatedEmbed, ephemeral=False)

            # * Add the forum to the database
            await reputation_forum.insert_one({
                "_guildID": interaction.guild.id,
                "_forumID": forum.id,
                "_forumCategory": categorie.id,
                "_forumName": channel_name,
                "_forumTopic": topic_name,
            })

    # * If forum remove manually delete the forum in the database
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, discord.ForumChannel):
            await reputation_forum.delete_one({"_forumID": channel.id})

    # * Update forum details
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if isinstance(after, discord.ForumChannel):
            # * Update forum name if changed
            if before.name != after.name:
                await reputation_forum.update_one({"_forumID": after.id}, {"$set": {"_forumName": after.name}})
            # * Update forum topic if changed
            if before.topic != after.topic:
                await reputation_forum.update_one({"_forumID": after.id}, {"$set": {"_forumTopic": after.topic}})
            # * Update forum category if changed
            if before.category_id != after.category_id:
                await reputation_forum.update_one({"_forumID": after.id}, {"$set": {"_forumCategory": after.category_id}})



async def setup(bot):
    await bot.add_cog(Forum(bot))

        