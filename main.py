# Description: This is the main file of the bot, it will be used to start the bot and load the cogs.

# * Import the necessary libraries
import os
from dotenv import load_dotenv

# * Import the necessary discord libraries
import discord
from discord.ext import commands

# * Load the environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')

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

if __name__ == '__main__':
    luffy.run(DISCORD_TOKEN) # type: ignore