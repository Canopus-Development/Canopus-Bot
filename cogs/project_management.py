import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import json
import datetime

class ProjectManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}
        self.load_tasks()

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            pass

    def save_tasks(self):
        with open('tasks.json', 'w') as f:
            json.dump(self.tasks, f)

    @app_commands.command()
    async def taskcreate(self, interaction: discord.Interaction, title: str, description: str, 
                        assignee: discord.Member, deadline: str):
        """Create a new task"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.tasks:
            self.tasks[guild_id] = []

        task_id = len(self.tasks[guild_id]) + 1
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "assignee": assignee.id,
            "creator": interaction.user.id,
            "deadline": deadline,
            "status": "In Progress"
        }
        
        self.tasks[guild_id].append(task)
        self.save_tasks()

        embed = discord.Embed(
            title=f"Task #{task_id}: {title}",
            description=description,
            color=discord.Color.blue()
        )
        embed.add_field(name="Assignee", value=assignee.mention)
        embed.add_field(name="Deadline", value=deadline)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def taskupdate(self, interaction: discord.Interaction, task_id: int, status: str):
        """Update task status"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.tasks:
            return await interaction.response.send_message("No tasks found.", ephemeral=True)

        for task in self.tasks[guild_id]:
            if task["id"] == task_id:
                task["status"] = status
                self.save_tasks()
                await interaction.response.send_message(f"Task #{task_id} status updated to: {status}")
                return

        await interaction.response.send_message("Task not found.", ephemeral=True)

    @app_commands.command()
    async def tasklist(self, interaction: discord.Interaction, status: Optional[str] = None):
        """List all tasks"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.tasks or not self.tasks[guild_id]:
            return await interaction.response.send_message("No tasks found.", ephemeral=True)

        embed = discord.Embed(title="Task List", color=discord.Color.blue())
        for task in self.tasks[guild_id]:
            if status and task["status"].lower() != status.lower():
                continue
            assignee = interaction.guild.get_member(task["assignee"])
            embed.add_field(
                name=f"#{task['id']}: {task['title']}",
                value=f"Status: {task['status']}\nAssignee: {assignee.mention if assignee else 'Unknown'}\nDeadline: {task['deadline']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def meeting(self, interaction: discord.Interaction, date: str, time: str, agenda: str, participants: str):
        """Schedule a meeting"""
        embed = discord.Embed(
            title="📅 Meeting Scheduled",
            description=f"**Date:** {date}\n**Time:** {time}\n\n**Agenda:**\n{agenda}\n\n**Participants:** {participants}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Scheduled by {interaction.user}")
        
        # Send meeting notification
        await interaction.response.send_message(embed=embed)
        
        # Optional: Set up reminder
        try:
            reminder_time = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            self.bot.loop.create_task(self.send_meeting_reminder(interaction.channel.id, reminder_time, embed))
        except ValueError:
            await interaction.followup.send("Could not set reminder: Invalid date/time format", ephemeral=True)

    async def send_meeting_reminder(self, channel_id, reminder_time, embed):
        """Send meeting reminder 15 minutes before"""
        now = datetime.datetime.now()
        if reminder_time > now:
            wait_time = (reminder_time - now).total_seconds() - 900  # 15 minutes before
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    reminder_embed = discord.Embed(
                        title="⏰ Meeting Reminder",
                        description="Meeting starting in 15 minutes!",
                        color=discord.Color.gold()
                    )
                    reminder_embed.add_field(name="Original Meeting Details", value=embed.description)
                    await channel.send(embed=reminder_embed)

    @app_commands.command()
    async def taskdelete(self, interaction: discord.Interaction, task_id: int):
        """Delete a task"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.tasks:
            return await interaction.response.send_message("No tasks found.", ephemeral=True)

        task_found = False
        for i, task in enumerate(self.tasks[guild_id]):
            if task["id"] == task_id:
                if task["creator"] == interaction.user.id or interaction.user.guild_permissions.administrator:
                    self.tasks[guild_id].pop(i)
                    self.save_tasks()
                    task_found = True
                    await interaction.response.send_message(f"Task #{task_id} has been deleted.")
                else:
                    await interaction.response.send_message("You can only delete tasks you created.", ephemeral=True)
                break

        if not task_found:
            await interaction.response.send_message("Task not found.", ephemeral=True)

    @app_commands.command()
    async def teamassign(self, interaction: discord.Interaction, team_name: str, member: discord.Member):
        """Assign a member to a team"""
        role = discord.utils.get(interaction.guild.roles, name=team_name)
        if not role:
            role = await interaction.guild.create_role(name=team_name, mentionable=True)
            
        await member.add_roles(role)
        
        embed = discord.Embed(
            title="Team Assignment",
            description=f"{member.mention} has been assigned to team {team_name}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def teamremove(self, interaction: discord.Interaction, team_name: str, member: discord.Member):
        """Remove a member from a team"""
        role = discord.utils.get(interaction.guild.roles, name=team_name)
        if role and role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"Removed {member.mention} from team {team_name}")
        else:
            await interaction.response.send_message(f"{member.mention} is not in team {team_name}", ephemeral=True)

    @app_commands.command()
    async def teamlist(self, interaction: discord.Interaction, team_name: str):
        """List all members in a team"""
        role = discord.utils.get(interaction.guild.roles, name=team_name)
        if not role:
            return await interaction.response.send_message("Team not found.", ephemeral=True)

        members = role.members
        if not members:
            return await interaction.response.send_message("No members in this team.", ephemeral=True)

        embed = discord.Embed(title=f"Team {team_name} Members", color=role.color)
        embed.description = "\n".join([member.mention for member in members])
        embed.set_footer(text=f"Total members: {len(members)}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProjectManagementCog(bot))
