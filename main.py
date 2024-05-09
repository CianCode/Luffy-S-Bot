# Description: This is the main file of the bot, it will be used to start the bot and load the cogs.

# * Import the necessary libraries
import os
import time
from dotenv import load_dotenv

# * Import the necessary discord libraries
import discord
from discord.ext import commands
from discord import app_commands

# * Load the environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX', "!")

# * Create the cog file manager
class CogManager(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def load(self) -> None:
        for root, _, files in os.walk('./cogs'):
            # * Skip the utils folder
            if 'utils' in root:
                continue
            for filename in files:
                # * Skip the files that start with __
                if filename.startswith('__'):
                    continue
                if filename.endswith('.py'):
                    try:
                        path = os.path.join(root, filename)[len("./cogs/"):][:-3].replace(os.path.sep, '.')
                        await luffy.load_extension(f'cogs.{path}')
                        print(f'🟢 SUCCES | Loaded the cog: {filename}')
                    except Exception as e:
                        print(f'❌ ERROR | {e}')

# * Creation of the bot class
class Luffy(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=PREFIX, intents=discord.Intents.all()) # type: ignore

    async def setup_hook(self) -> None:
        await CogManager(self).load()
        await self.tree.sync()

    async def on_ready(self) -> None:
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"Thousand Sunny!"))

        print(f'Logged in as {self.user}')

    async def on_connect(self) -> None:
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"Initialisation..."))

luffy = Luffy()

# * Error handling
@luffy.tree.error
async def on_app_command_error(ctx, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(title="⚠️ Commande en rechargement",
                                  description=f"Cette commande est en rechargement.\nVeuillez réessayer <t:{int(time.time() + error.retry_after)}:R>.",
                                  color=0xffdd63)
            await ctx.response.send_message(embed=embed)
        elif isinstance(error, app_commands.MissingPermissions):
            missing_perms = ', '.join(error.missing_permissions)
            embed = discord.Embed(title="⚠️ Permission(s) manquante(s)",
                                  description=f"Permission(s) manquante(s): `{missing_perms}`.\nVous avez besoin de cette (ou ces) permission(s).",
                                  color=0xffdd63)
            await ctx.response.send_message(embed=embed)
        elif isinstance(error, app_commands.MissingRole):
            missing_role = error.missing_role
            embed = discord.Embed(title="⚠️ Rôle requis manquant",
                                  description=f"Rôle manquant: <@&{missing_role}>.\nVous avez besoin de ce rôle.",
                                  color=0xffdd63)
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.response.send_message(
                embed=discord.Embed(
                    title="Erreur inconnue au bataillon",
                    description=f"> {error}",
                    color=0xffdd63
                ))
            raise error

if __name__ == '__main__':
    luffy.run(DISCORD_TOKEN) # type: ignore