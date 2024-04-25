# Description: Add reputation points to a member

# * Import the necessary discord libraries
from uu import Error
import discord
from discord import app_commands
from discord.ext import commands

from ..utils.database import reputation_members, reputation_forum
from ..utils import colorEmbed

from .__reputation_updater import update_reputation_role

class ReputationForumView(discord.ui.Select):
    def __init__(self, bot, options):
        super().__init__(placeholder='Select a member', options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):

        # * Get the selected member
        selected_member_id = interaction.data['values'][0]
        selected_member_id = int(selected_member_id)
        member = interaction.guild.get_member(selected_member_id)

        # * Check if the member exists in the database
        memberData = await reputation_members.find_one({"_guildID": interaction.guild_id,"_memberID": selected_member_id})

        # * Create a member in the database if it doesn't exist
        if memberData is None:
            await reputation_members.insert_one({"_guildID": interaction.guild_id, "_memberID": member.id, "_reputationPoints": 0})

        # * Add reputation points to the selected member
        reputation_add = 100

        # * Update the reputation points
        await reputation_members.update_one({"_guildID": interaction.guild_id, "_memberID": selected_member_id}, {"$inc": {"_reputationPoints": reputation_add}})

        await update_reputation_role(interaction.guild, member, "add")
        
        # * Create an embed
        GiveReputationEmbed = discord.Embed(
            description=f"{member.mention} a été sélectionné comme la personne à avoir aider le plus dans se thread \n Il a reçu {reputation_add} point de reputation !?",
            color=colorEmbed.generate_random_color()
        ).set_author(
            name="Resolved Thread",
            icon_url=interaction.user.display_avatar
        )

        await interaction.response.send_message(embed=GiveReputationEmbed, ephemeral=False)

        # * Close the thread
        forum = interaction.channel.parent
        all_tags = forum.available_tags
        tag = discord.utils.get(all_tags, name="Résolu")

        await interaction.channel.edit(locked=True, applied_tags=[tag])

class ReputationForum(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="resolved", description="Close a resolved thread and give reputation to the member who helped the most")
    async def resolved(self, interaction: discord.Interaction):
        # * Create Embeds
        AskEmbed = discord.Embed(
            description="Sélectionnez un membre à remercier pour vous avoir aider !",
            color=colorEmbed.generate_random_color()
        ).set_author(
            name="Resolved Thread",
            icon_url=interaction.user.display_avatar
        )
        ErrorThreadEmbed = discord.Embed(
            description="Cette commande ne peut être utilisée que dans un channel de thread !",
            color=colorEmbed.Red
        )
        ErrorThreadDtabaseEmbed = discord.Embed(
            description="Ce thread n'existe pas dans la base de données !",
            color=colorEmbed.Red
        )
        ErrorPermissionEmbed = discord.Embed(
            description="Vous n'êtes pas autorisé à fermer ce thread !",
            color=colorEmbed.Red
        )
        ErrorParticipantEmbed = discord.Embed(
            description="Il n'y a pas de participants dans ce thread !",
            color=colorEmbed.Red
        )

        # * Check if the channel is a thread
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message(embed=ErrorThreadEmbed, ephemeral=True)
            return

        # * Database data
        database_data = await reputation_forum.find_one({"_guildID": interaction.guild_id, "_forumID": interaction.channel.parent_id})
        
        # * Get the forum id and author id
        forum_id = interaction.channel.parent_id
        author_id = interaction.user.id

        # * Check if the database data is None or the forum id is different
        if database_data is None or database_data["_forumID"] != forum_id:
            await interaction.response.send_message(embed=ErrorThreadDtabaseEmbed, ephemeral=True)
            return
        
        # * Check if the author id is different from the channel owner id
        if author_id != interaction.channel.owner_id or interaction.user.guild_permissions.administrator == False :
            await interaction.response.send_message(embed=ErrorPermissionEmbed, ephemeral=True)
            return

        # * Get all the members in the channel excluding the author and the bots
        members = await interaction.channel.fetch_members()
        participants = set()
        for member in members:
            membersId = interaction.guild.get_member(member.id)
            participants.add(membersId)

        if len(participants) == 1:
            await interaction.response.send_message(embed=ErrorParticipantEmbed, ephemeral=True)
            return

        # * Create a select menu with all the participants
        options = [
            discord.SelectOption(label=participant.display_name, value=str(participant.id), emoji="👲")
            for participant in participants
            if participant.id != interaction.channel.owner_id and not participant.bot
        ]

        # * Create a view with the select menu
        select = ReputationForumView(self.bot, options)
        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message(embed=AskEmbed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ReputationForum(bot))
