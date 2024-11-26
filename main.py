import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class CanopusBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=discord.Intents.all(),
            application_id=int(os.getenv('APP_ID')),
            help_command=None,  # Remove default help command
        )
        self.initial_extensions = [
            'cogs.moderation',
            'cogs.welcome',
            'cogs.admin',
            'cogs.utility',
            'cogs.project_management',
            'cogs.professional',
            'cogs.tickets',
            'cogs.help', 
            'events.on_message'
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        
        # Remove default help command and sync all commands
        await self.tree.sync()

    async def on_ready(self):
        print(f"{self.user} is ready!")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/help | Canopus Development"
            )
        )

bot = CanopusBot()
bot.run(os.getenv('BOT_TOKEN'))
