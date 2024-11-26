import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List

class CategorySelect(discord.ui.Select):
    def __init__(self, help_command):
        self.help_command = help_command
        options = [
            discord.SelectOption(
                label="Moderation",
                description="Server moderation commands",
                emoji="🛡️",
                value="moderation"
            ),
            discord.SelectOption(
                label="Administration",
                description="Server management commands",
                emoji="⚙️",
                value="admin"
            ),
            discord.SelectOption(
                label="Utility",
                description="General utility commands",
                emoji="🔧",
                value="utility"
            ),
            discord.SelectOption(
                label="Project Management",
                description="Task and project commands",
                emoji="📊",
                value="project"
            ),
            discord.SelectOption(
                label="Professional",
                description="Team collaboration commands",
                emoji="👥",
                value="professional"
            ),
            discord.SelectOption(
                label="Tickets",
                description="Ticket system commands",
                emoji="🎫",
                value="tickets"
            )
        ]
        super().__init__(
            placeholder="Select a category...",
            options=options,
            custom_id="category_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await self.help_command.show_category(interaction, self.values[0])

class SupportButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.link,
            label="Support",
            emoji="❓",
            url="https://discord.gg/JUhv27kzcJ"
        )

class HomeButton(discord.ui.Button):
    def __init__(self, help_command):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Home",
            emoji="🏠"
        )
        self.help_command = help_command

    async def callback(self, interaction: discord.Interaction):
        await self.help_command.show_home_page(interaction)

class HelpView(discord.ui.View):
    def __init__(self, help_command):
        super().__init__(timeout=60)
        self.help_command = help_command
        self.add_item(CategorySelect(help_command))
        self.add_item(HomeButton(help_command))
        self.add_item(SupportButton())

class HelpCog(commands.GroupCog, name="help"):
    def __init__(self, bot):
        self.bot = bot
        self.command_categories = {
            "moderation": {
                "emoji": "🛡️",
                "description": "Keep your server safe and organized",
                "commands": [
                    ("kick", "Kick a member from the server"),
                    ("ban", "Ban a member from the server"),
                    ("timeout", "Timeout a member temporarily"),
                    ("warn", "Warn a member"),
                    ("mute", "Mute a member"),
                    ("unmute", "Unmute a member"),
                    ("purge", "Delete multiple messages"),
                    ("lockchannel", "Lock a channel"),
                    ("unlockchannel", "Unlock a channel"),
                    ("modlog", "View moderation logs")
                ]
            },
            "admin": {
                "emoji": "⚙️",
                "description": "Manage your server effectively",
                "commands": [
                    ("createchannel", "Create a new channel"),
                    ("deletechannel", "Delete a channel"),
                    ("createrole", "Create a new role"),
                    ("deleterole", "Delete a role"),
                    ("serverinfo", "View server information"),
                    ("slowmode", "Set channel slowmode"),
                    ("announce", "Make an announcement"),
                    ("setnickname", "Change member nickname"),
                    ("permissions", "Manage channel permissions")
                ]
            },
            "utility": {
                "emoji": "🔧",
                "description": "General utility commands for everyone",
                "commands": [
                    ("poll", "Create a poll"),
                    ("remindme", "Set a reminder"),
                    ("userinfo", "View user information"),
                    ("roleinfo", "View role information"),
                    ("pinmessage", "Pin a message"),
                    ("reactionrole", "Create reaction roles")
                ]
            },
            "project": {
                "emoji": "📊",
                "description": "Manage projects and tasks",
                "commands": [
                    ("taskcreate", "Create a new task"),
                    ("taskupdate", "Update task status"),
                    ("tasklist", "View all tasks"),
                    ("taskdelete", "Delete a task"),
                    ("meeting", "Schedule a meeting"),
                    ("teamassign", "Add member to team"),
                    ("teamremove", "Remove member from team"),
                    ("teamlist", "List team members")
                ]
            },
            "professional": {
                "emoji": "👥",
                "description": "Professional team collaboration",
                "commands": [
                    ("standup", "Conduct team standup"),
                    ("standupreport", "Generate standup report"),
                    ("faq", "Manage FAQ entries"),
                    ("feedback", "Submit feedback"),
                    ("resources", "Access resources"),
                    ("milestone", "Announce milestone"),
                    ("teaminfo", "View team info"),
                    ("linkproject", "Link project resources")
                ]
            },
            "tickets": {
                "emoji": "🎫",
                "description": "Ticket system management",
                "commands": [
                    ("ticketsetup", "Set up ticket system"),
                    ("closeticket", "Close a ticket"),
                    ("addticketadmin", "Add ticket admin"),
                    ("ticketstats", "View ticket statistics")
                ]
            }
        }
        super().__init__()

    @app_commands.command(name="help")
    async def help_command(self, interaction: discord.Interaction, command: Optional[str] = None):
        """Get help with bot commands"""
        if command:
            await self.show_command_help(interaction, command)
        else:
            await self.show_home_page(interaction)

    @app_commands.command(name="category")
    async def category_help(self, interaction: discord.Interaction, category: str):
        """Get help for a specific category"""
        await self.show_category(interaction, category.lower())

    async def show_home_page(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Canopus Bot Help",
            description="Welcome to the help menu! Select a category below or use `/help category <name>`.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        for category, data in self.command_categories.items():
            embed.add_field(
                name=f"{data['emoji']} {category.title()}",
                value=data['description'],
                inline=True
            )

        embed.set_footer(text="Use /help <command> for detailed command information")
        
        if isinstance(interaction, discord.Interaction):
            if interaction.response.is_done():
                await interaction.message.edit(embed=embed, view=HelpView(self))
            else:
                await interaction.response.send_message(embed=embed, view=HelpView(self))

    async def show_category(self, interaction: discord.Interaction, category: str):
        if category not in self.command_categories:
            return await interaction.response.send_message("Category not found!", ephemeral=True)

        data = self.command_categories[category]
        embed = discord.Embed(
            title=f"{data['emoji']} {category.title()} Commands",
            description=data['description'],
            color=discord.Color.blue()
        )

        # Add commands
        for cmd, desc in data['commands']:
            embed.add_field(
                name=f"/{cmd}",
                value=desc,
                inline=False
            )

        embed.set_footer(text="Use /help <command> for more details")
        await interaction.response.edit_message(embed=embed, view=HelpView(self))

    async def show_command_help(self, interaction: discord.Interaction, command_name: str):
        command = self.bot.tree.get_command(command_name)
        if not command:
            return await interaction.response.send_message(
                f"Command `{command_name}` not found!",
                ephemeral=True
            )

        embed = discord.Embed(
            title=f"Command: /{command.name}",
            description=command.description or "No description provided",
            color=discord.Color.green()
        )

        # Add parameters
        if hasattr(command, 'parameters'):
            params = []
            for param in command.parameters:
                param_type = param.type.__str__().split('.')[-1]
                required = "Required" if param.required else "Optional"
                params.append(f"`{param.name}` ({param_type}) - {required}")
            
            if params:
                embed.add_field(
                    name="Parameters",
                    value="\n".join(params),
                    inline=False
                )

        # Add permissions
        if hasattr(command, 'checks'):
            perms = []
            for check in command.checks:
                if hasattr(check, 'permission'):
                    perms.append(str(check.permission).replace('_', ' ').title())
            
            if perms:
                embed.add_field(
                    name="Required Permissions",
                    value="\n.join(perms)",
                    inline=False
                )

        embed.set_footer(text="<> = Required, [] = Optional")
        await interaction.response.send_message(embed=embed, view=HelpView(self))

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
