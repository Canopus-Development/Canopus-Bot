
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channels = {}  # guild_id: channel_id

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id not in self.welcome_channels:
            return

        channel = member.guild.get_channel(self.welcome_channels[member.guild.id])
        if not channel:
            return

        embed = discord.Embed(
            title="Welcome!",
            description=f"Welcome {member.mention} to {member.guild.name}! 🎉",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Member Count", value=f"We now have {member.guild.member_count} members!")
        
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id not in self.welcome_channels:
            return

        channel = member.guild.get_channel(self.welcome_channels[member.guild.id])
        if not channel:
            return

        embed = discord.Embed(
            title="Goodbye!",
            description=f"**{member}** has left the server 👋",
            color=discord.Color.red()
        )
        
        await channel.send(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Set the welcome channel for join/leave messages"""
        target_channel = channel or interaction.channel
        self.welcome_channels[interaction.guild.id] = target_channel.id
        
        embed = discord.Embed(
            title="Welcome Channel Set",
            description=f"Welcome messages will now be sent in {target_channel.mention}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def testwelcome(self, interaction: discord.Interaction):
        """Test the welcome message"""
        if interaction.guild.id not in self.welcome_channels:
            return await interaction.response.send_message("Welcome channel not set! Use /setwelcome first.", ephemeral=True)

        member = interaction.user
        channel = interaction.guild.get_channel(self.welcome_channels[interaction.guild.id])
        
        if not channel:
            return await interaction.response.send_message("Welcome channel not found!", ephemeral=True)

        embed = discord.Embed(
            title="Welcome! (Test)",
            description=f"Welcome {member.mention} to {member.guild.name}! 🎉",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Member Count", value=f"We now have {member.guild.member_count} members!")
        embed.set_footer(text="This is a test message")
        
        await channel.send(embed=embed)
        await interaction.response.send_message("Test welcome message sent!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))