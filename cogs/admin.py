import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Union

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def createchannel(self, interaction: discord.Interaction, name: str, category: Optional[discord.CategoryChannel] = None):
        """Create a new text channel"""
        channel = await interaction.guild.create_text_channel(name=name, category=category)
        await interaction.response.send_message(f"Created channel {channel.mention}")

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def createrole(self, interaction: discord.Interaction, name: str, color: Optional[str] = None):
        """Create a new role"""
        try:
            if color:
                color = discord.Color.from_str(color)
            role = await interaction.guild.create_role(name=name, color=color)
            await interaction.response.send_message(f"Created role {role.mention}")
        except ValueError:
            await interaction.response.send_message("Invalid color format! Use hex color (e.g., #FF0000)", ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def serverinfo(self, interaction: discord.Interaction):
        """Display server information"""
        guild = interaction.guild
        embed = discord.Embed(
            title=f"{guild.name} Information",
            color=discord.Color.blue()
        )
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        """Set slowmode for the current channel"""
        if not 0 <= seconds <= 21600:
            return await interaction.response.send_message("Slowmode must be between 0 and 21600 seconds", ephemeral=True)
        
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message("Slowmode disabled")
        else:
            await interaction.response.send_message(f"Slowmode set to {seconds} seconds")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel] = None):
        """Make an announcement"""
        target_channel = channel or interaction.channel
        embed = discord.Embed(
            title="Announcement",
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Announced by {interaction.user}")
        
        await target_channel.send(embed=embed)
        if channel:
            await interaction.response.send_message("Announcement sent!", ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def deletechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Delete a channel"""
        await channel.delete()
        await interaction.response.send_message(f"Channel {channel.name} has been deleted")

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def deleterole(self, interaction: discord.Interaction, role: discord.Role):
        """Delete a role"""
        await role.delete()
        await interaction.response.send_message(f"Role {role.name} has been deleted")

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def setnickname(self, interaction: discord.Interaction, member: discord.Member, nickname: str):
        """Set a member's nickname"""
        await member.edit(nick=nickname)
        await interaction.response.send_message(f"Changed {member.name}'s nickname to {nickname}")

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def permissions(self, interaction: discord.Interaction, channel: discord.TextChannel, 
                         target: Union[discord.Role, discord.Member], *, perms: str):
        """Manage channel permissions"""
        try:
            perms_dict = dict(x.split('=') for x in perms.split(','))
            overwrite = channel.overwrites_for(target)
            
            for perm, value in perms_dict.items():
                if hasattr(discord.Permissions, perm):
                    setattr(overwrite, perm, value.lower() == 'true')
            
            await channel.set_permissions(target, overwrite=overwrite)
            await interaction.response.send_message(f"Updated permissions for {target.name} in {channel.name}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
