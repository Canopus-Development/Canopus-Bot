import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import datetime
import json
import os

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}
        self.mod_logs = {}
        self._load_data()

    def _load_data(self):
        if os.path.exists('warnings.json'):
            with open('warnings.json', 'r') as f:
                self.warnings = json.load(f)
        if os.path.exists('mod_logs.json'):
            with open('mod_logs.json', 'r') as f:
                self.mod_logs = json.load(f)

    def _save_data(self):
        with open('warnings.json', 'w') as f:
            json.dump(self.warnings, f)
        with open('mod_logs.json', 'w') as f:
            json.dump(self.mod_logs, f)

    def _log_action(self, guild_id: str, action: str, moderator: str, target: str, reason: str):
        if str(guild_id) not in self.mod_logs:
            self.mod_logs[str(guild_id)] = []
        self.mod_logs[str(guild_id)].append({
            'action': action,
            'moderator': moderator,
            'target': target,
            'reason': reason,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        self._save_data()

    @app_commands.command()
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
        """Kick a member from the server"""
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't kick this user!", ephemeral=True)
        
        reason = reason or f"Kicked by {interaction.user}"
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title="Member Kicked",
            description=f"**{member}** was kicked by {interaction.user.mention}\nReason: {reason}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
        """Ban a member from the server"""
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't ban this user!", ephemeral=True)
        
        reason = reason or f"Banned by {interaction.user}"
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title="Member Banned",
            description=f"**{member}** was banned by {interaction.user.mention}\nReason: {reason}",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, unit: str, reason: Optional[str] = None):
        """Timeout a member (duration in minutes/hours/days)"""
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't timeout this user!", ephemeral=True)

        unit_map = {"m": 1, "h": 60, "d": 1440}
        if unit.lower() not in unit_map:
            return await interaction.response.send_message("Invalid unit! Use m (minutes), h (hours), or d (days)", ephemeral=True)

        minutes = duration * unit_map[unit.lower()]
        until = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
        
        reason = reason or f"Timed out by {interaction.user}"
        await member.timeout(until, reason=reason)
        
        embed = discord.Embed(
            title="Member Timed Out",
            description=f"**{member}** was timed out for {duration}{unit}\nReason: {reason}",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        """Delete a specified number of messages"""
        if amount < 1 or amount > 100:
            return await interaction.response.send_message("Please specify a number between 1 and 100", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Warn a member"""
        guild_id = str(interaction.guild.id)
        member_id = str(member.id)
        
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if member_id not in self.warnings[guild_id]:
            self.warnings[guild_id][member_id] = []
            
        self.warnings[guild_id][member_id].append({
            'reason': reason,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        self._save_data()
        self._log_action(guild_id, 'warn', str(interaction.user), str(member), reason)
        
        await interaction.response.send_message(f"Warned {member.mention} for: {reason}")

    @app_commands.command()
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: Optional[int] = None):
        """Mute a member"""
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)
        
        await member.add_roles(muted_role)
        self._log_action(str(interaction.guild.id), 'mute', str(interaction.user), str(member), f"Duration: {duration if duration else 'indefinite'}")
        
        await interaction.response.send_message(f"Muted {member.mention}")

    @app_commands.command()
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Unmute a member"""
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            self._log_action(str(interaction.guild.id), 'unmute', str(interaction.user), str(member), "N/A")
            await interaction.response.send_message(f"Unmuted {member.mention}")
        else:
            await interaction.response.send_message(f"{member.mention} is not muted", ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lockchannel(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Lock a channel"""
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        self._log_action(str(interaction.guild.id), 'lock', str(interaction.user), channel.name, "N/A")
        await interaction.response.send_message(f"Locked {channel.mention}")

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlockchannel(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Unlock a channel"""
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=None)
        self._log_action(str(interaction.guild.id), 'unlock', str(interaction.user), channel.name, "N/A")
        await interaction.response.send_message(f"Unlocked {channel.mention}")

    @app_commands.command()
    @app_commands.checks.has_permissions(view_audit_log=True)
    async def modlog(self, interaction: discord.Interaction, limit: int = 10):
        """View recent moderation actions"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.mod_logs or not self.mod_logs[guild_id]:
            return await interaction.response.send_message("No moderation logs found", ephemeral=True)
        
        logs = self.mod_logs[guild_id][-limit:]
        embed = discord.Embed(title="Moderation Logs", color=discord.Color.blue())
        for log in logs:
            embed.add_field(
                name=f"{log['action'].upper()} - {log['timestamp']}",
                value=f"Moderator: {log['moderator']}\nTarget: {log['target']}\nReason: {log['reason']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
