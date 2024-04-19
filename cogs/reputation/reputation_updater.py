import discord
from discord.ext import commands
from ..utils.database import reputation_members, reputation_roles

class ReputationUpdater(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def update_member_role(self, member: discord.Member):
        # Retrieve the member's reputation points
        reputation = await reputation_members.find_one({"_memberID": member.id})
        if reputation is not None:
            reputation_points = reputation["_reputationPoints"]

            # Get all reputation roles and sort by reputation points (high to low)
            roles = await reputation_roles.find({}).to_list(length=None)
            sorted_roles = sorted(roles, key=lambda x: x['_reputationPoints'], reverse=True)

            # Find the appropriate role based on reputation points
            for role_data in sorted_roles:
                role_id = role_data["_roleID"]
                role = member.guild.get_role(role_id)
                if role is not None and reputation_points >= role_data["_reputationPoints"]:
                    # Remove other reputation roles and add the appropriate one
                    await member.remove_roles(*[r for r in member.roles if r.id != role_id])
                    await member.add_roles(role)
                    break

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            # Member roles have been updated, trigger reputation role update
            await self.update_member_role(after)


async def setup(bot):
    await bot.add_cog(ReputationUpdater(bot))