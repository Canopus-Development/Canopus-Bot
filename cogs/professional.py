import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import json
import datetime
import asyncio

class ProfessionalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faq_data = {}
        self.resources = {}
        self._load_data()

    def _load_data(self):
        try:
            with open('faq.json', 'r') as f:
                self.faq_data = json.load(f)
            with open('resources.json', 'r') as f:
                self.resources = json.load(f)
        except FileNotFoundError:
            pass

    def _save_data(self):
        with open('faq.json', 'w') as f:
            json.dump(self.faq_data, f)
        with open('resources.json', 'w') as f:
            json.dump(self.resources, f)

    @app_commands.command()
    async def standup(self, interaction: discord.Interaction, team_name: str, type: str = "daily"):
        """Conduct a team standup"""
        embed = discord.Embed(title=f"{team_name} {type.capitalize()} Standup", color=discord.Color.blue())
        embed.add_field(name="Format", value="Please share:\n1. What you did\n2. What you plan to do\n3. Any blockers")
        
        await interaction.response.send_message(embed=embed)
        
        def check(m):
            return m.channel == interaction.channel and not m.author.bot
        
        try:
            messages = []
            while True:
                msg = await self.bot.wait_for('message', timeout=300.0, check=check)
                if msg.content.lower() == 'done':
                    break
                messages.append(f"**{msg.author.display_name}**:\n{msg.content}")
        except asyncio.TimeoutError:
            await interaction.followup.send("Standup timed out.")
        else:
            summary = discord.Embed(title="Standup Summary", description="\n\n".join(messages))
            await interaction.followup.send(embed=summary)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    async def faq(self, interaction: discord.Interaction, action: str, topic: str, content: Optional[str] = None):
        """Manage FAQ entries"""
        guild_id = str(interaction.guild.id)
        
        if action.lower() == "add":
            if guild_id not in self.faq_data:
                self.faq_data[guild_id] = {}
            self.faq_data[guild_id][topic] = content
            self._save_data()
            await interaction.response.send_message(f"Added FAQ entry for: {topic}")
            
        elif action.lower() == "show":
            if guild_id in self.faq_data and topic in self.faq_data[guild_id]:
                embed = discord.Embed(title=f"FAQ: {topic}", description=self.faq_data[guild_id][topic])
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("FAQ entry not found.", ephemeral=True)

    @app_commands.command()
    async def feedback(self, interaction: discord.Interaction, topic: str, details: str):
        """Submit feedback"""
        embed = discord.Embed(
            title="Feedback Submitted",
            description=f"Topic: {topic}\n\n{details}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"From: {interaction.user}")
        
        # Send to a designated feedback channel if set up
        await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)
        
        # Optional: Log feedback in a specific channel
        if hasattr(self.bot, 'feedback_channel'):
            await self.bot.feedback_channel.send(embed=embed)

    @app_commands.command()
    async def resources(self, interaction: discord.Interaction, topic: str):
        """Access learning resources"""
        guild_id = str(interaction.guild.id)
        if guild_id in self.resources and topic in self.resources[guild_id]:
            embed = discord.Embed(title=f"Resources: {topic}", color=discord.Color.blue())
            for resource in self.resources[guild_id][topic]:
                embed.add_field(name=resource['name'], value=resource['url'], inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No resources found for this topic.", ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    async def milestone(self, interaction: discord.Interaction, milestone_name: str, project_name: str, description: Optional[str] = None):
        """Announce a project milestone"""
        embed = discord.Embed(
            title=f"🎉 Milestone Achieved: {milestone_name}",
            description=f"Project: {project_name}\n\n{description or 'No description provided'}",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Announced by {interaction.user}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def teaminfo(self, interaction: discord.Interaction, project_name: str):
        """Display team/project information"""
        role = discord.utils.get(interaction.guild.roles, name=project_name)
        if not role:
            return await interaction.response.send_message("Project/Team not found.", ephemeral=True)

        embed = discord.Embed(title=f"Project: {project_name}", color=role.color)
        members = role.members
        leads = [m for m in members if any(r.name.lower().endswith('lead') for r in m.roles)]
        developers = [m for m in members if m not in leads]

        if leads:
            embed.add_field(name="Team Leads", value="\n".join(m.mention for m in leads), inline=False)
        if developers:
            embed.add_field(name="Team Members", value="\n".join(m.mention for m in developers), inline=False)
        
        embed.set_footer(text=f"Total members: {len(members)}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def linkproject(self, interaction: discord.Interaction, project_name: str, url: str):
        """Link project resources"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.resources:
            self.resources[guild_id] = {}
        
        if project_name not in self.resources[guild_id]:
            self.resources[guild_id][project_name] = []
            
        self.resources[guild_id][project_name].append({
            'name': 'Project Link',
            'url': url
        })
        self._save_data()
        
        embed = discord.Embed(
            title=f"Project Link Added: {project_name}",
            description=f"[Click here to view]({url})",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def standupreport(self, interaction: discord.Interaction, team_name: str):
        """Generate a standup report for the past week"""
        # Get all standups from the past week
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        
        embed = discord.Embed(
            title=f"{team_name} Weekly Standup Report",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Summary",
            value="Weekly team progress report\nPeriod: Last 7 days",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfessionalCog(bot))
