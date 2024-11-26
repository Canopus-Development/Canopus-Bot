import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional
import datetime
import asyncio
import json

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = []
        self.reaction_roles = {}
        self.load_reaction_roles()
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    def load_reaction_roles(self):
        try:
            with open('reaction_roles.json', 'r') as f:
                self.reaction_roles = json.load(f)
        except FileNotFoundError:
            pass

    def save_reaction_roles(self):
        with open('reaction_roles.json', 'w') as f:
            json.dump(self.reaction_roles, f)

    @app_commands.command()
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, 
                  option3: Optional[str] = None, option4: Optional[str] = None):
        """Create a poll with up to 4 options"""
        options = [option1, option2]
        if option3: options.append(option3)
        if option4: options.append(option4)
        
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
        
        description = question + "\n\n" + "\n".join(f"{emojis[i]} {opt}" for i, opt in enumerate(options))
        embed = discord.Embed(title="Poll", description=description, color=discord.Color.blue())
        
        msg = await interaction.channel.send(embed=embed)
        for i in range(len(options)):
            await msg.add_reaction(emojis[i])
        await interaction.response.send_message("Poll created!", ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reactionrole(self, interaction: discord.Interaction, message: str, role: discord.Role, emoji: str):
        """Create a reaction role message"""
        embed = discord.Embed(description=message, color=discord.Color.green())
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction(emoji)
        
        self.reaction_roles[str(msg.id)] = {
            "role_id": role.id,
            "emoji": emoji
        }
        self.save_reaction_roles()
        
        await interaction.response.send_message("Reaction role created!", ephemeral=True)

    @app_commands.command()
    async def remindme(self, interaction: discord.Interaction, time: int, unit: str, message: str):
        """Set a reminder"""
        unit_map = {"m": 60, "h": 3600, "d": 86400}
        if unit.lower() not in unit_map:
            return await interaction.response.send_message("Invalid unit! Use m (minutes), h (hours), or d (days)", ephemeral=True)
        
        seconds = time * unit_map[unit.lower()]
        reminder_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
        
        self.reminders.append({
            "user_id": interaction.user.id,
            "channel_id": interaction.channel.id,
            "message": message,
            "time": reminder_time.timestamp()
        })
        
        await interaction.response.send_message(f"I'll remind you about '{message}' in {time}{unit}")

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        now = datetime.datetime.utcnow().timestamp()
        to_remove = []
        
        for reminder in self.reminders:
            if reminder["time"] <= now:
                channel = self.bot.get_channel(reminder["channel_id"])
                user = self.bot.get_user(reminder["user_id"])
                if channel and user:
                    await channel.send(f"{user.mention}, reminder: {reminder['message']}")
                to_remove.append(reminder)
        
        for reminder in to_remove:
            self.reminders.remove(reminder)

    @app_commands.command()
    async def userinfo(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Display information about a user"""
        member = member or interaction.user
        embed = discord.Embed(color=member.color)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
        embed.add_field(name="Registered", value=member.created_at.strftime("%Y-%m-%d"))
        embed.add_field(name="Roles", value=" ".join([r.mention for r in member.roles[1:]]) or "None")
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Display information about a role"""
        embed = discord.Embed(title=f"Role: {role.name}", color=role.color)
        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(name="Mentionable", value=role.mentionable)
        embed.add_field(name="Created", value=role.created_at.strftime("%Y-%m-%d"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    async def pinmessage(self, interaction: discord.Interaction, message_id: str):
        """Pin a message in the channel"""
        try:
            message = await interaction.channel.fetch_message(int(message_id))
            await message.pin()
            await interaction.response.send_message("Message pinned!", ephemeral=True)
        except:
            await interaction.response.send_message("Couldn't find that message.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
