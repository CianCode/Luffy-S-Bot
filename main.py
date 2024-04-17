# * Import the necessary libraries
import os
from dotenv import load_dotenv

# * Import the necessary discord libraries
import discord
from discord.ext import commands

# * Load the environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
PREFIX = os.getenv('PREFIX')

# TODO: Add the database connection using pymongo

# * Create the cog file manager
class Cogs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name='on_ready')
    async def loader(self) -> None:
        for root, _, files in os.walk('./cogs'):
            for filename in files:
                if filename.endswith('.py'):
                    try:
                        path = os.path.join(root, filename)[len("./cogs/"):][:-3].replace(os.path.sep, '.')
                        await self.bot.load_extension(f'cogs.{path}')
                        print(f'🟢 SUCCES | Loaded the cog: {filename}')
                    except Exception as e:
                        print(f'❌ ERROR | {e}')


# * Creation of the bot class
class Luffy(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=PREFIX, intents=discord.Intents.all()) # type: ignore

    async def setup_hook(self) -> None:
        await self.add_cog(Cogs(self))

        await self.tree.sync()

    async def on_ready(self) -> None:
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"Hello world!"))

        print(f'Logged in as {self.user}')
        print(f'--------------------------')

    async def on_connect(self) -> None:
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"Initialisation..."))

luffy = Luffy()

if __name__ == '__main__':
    luffy.run(DISCORD_TOKEN) # type: ignore