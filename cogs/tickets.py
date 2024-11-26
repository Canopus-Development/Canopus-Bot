import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import json
import asyncio

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_data = {}
        self.load_ticket_data()

    def load_ticket_data(self):
        try:
            with open('tickets.json', 'r') as f:
                self.ticket_data = json.load(f)
        except FileNotFoundError:
            self.ticket_data = {}

    def save_ticket_data(self):
        with open('tickets.json', 'w') as f:
            json.dump(self.ticket_data, f)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketsetup(self, interaction: discord.Interaction, category: Optional[discord.CategoryChannel] = None):
        """Setup the ticket system"""
        guild_id = str(interaction.guild.id)
        
        # Create ticket category if not specified
        if not category:
            category = await interaction.guild.create_category("Tickets")
        
        # Create support role if it doesn't exist
        support_role = discord.utils.get(interaction.guild.roles, name="Ticket Support")
        if not support_role:
            support_role = await interaction.guild.create_role(
                name="Ticket Support",
                color=discord.Color.blue(),
                reason="Ticket System Setup"
            )

        # Save ticket configuration
        self.ticket_data[guild_id] = {
            "category_id": category.id,
            "support_role_id": support_role.id,
            "ticket_counter": 0,
            "active_tickets": {}
        }
        self.save_ticket_data()

        # Create ticket creation channel
        embed = discord.Embed(
            title="🎫 Create a Ticket",
            description="Click the button below to create a support ticket",
            color=discord.Color.blue()
        )
        
        class TicketButton(discord.ui.Button):
            def __init__(self):
                super().__init__(
                    label="Create Ticket",
                    style=discord.ButtonStyle.primary,
                    emoji="🎫"
                )

            async def callback(self, button_interaction: discord.Interaction):
                await self.view.cog.create_ticket(button_interaction)

        view = discord.ui.View(timeout=None)
        view.add_item(TicketButton())
        view.cog = self

        await interaction.response.send_message(embed=embed, view=view)

    async def create_ticket(self, interaction: discord.Interaction):
        """Create a new ticket channel"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.ticket_data:
            return await interaction.response.send_message("Ticket system not set up!", ephemeral=True)

        # Increment ticket counter
        self.ticket_data[guild_id]["ticket_counter"] += 1
        ticket_number = self.ticket_data[guild_id]["ticket_counter"]
        
        # Get category and create channel
        category = interaction.guild.get_channel(self.ticket_data[guild_id]["category_id"])
        support_role = interaction.guild.get_role(self.ticket_data[guild_id]["support_role_id"])

        ticket_channel = await interaction.guild.create_text_channel(
            f"ticket-{ticket_number}",
            category=category,
            topic=f"Ticket for {interaction.user}"
        )

        # Set permissions
        await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(support_role, read_messages=True, send_messages=True)

        # Create ticket embed
        embed = discord.Embed(
            title=f"Ticket #{ticket_number}",
            description="Support will be with you shortly.\nTo close this ticket, use `/closeticket`",
            color=discord.Color.green()
        )
        embed.add_field(name="Created by", value=interaction.user.mention)

        class TicketClose(discord.ui.Button):
            def __init__(self):
                super().__init__(
                    label="Close Ticket",
                    style=discord.ButtonStyle.danger,
                    emoji="🔒"
                )

            async def callback(self, button_interaction: discord.Interaction):
                await self.view.cog.close_ticket(button_interaction, ticket_channel)

        view = discord.ui.View(timeout=None)
        view.add_item(TicketClose())
        view.cog = self

        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Created ticket {ticket_channel.mention}", ephemeral=True)

        # Save ticket data
        self.ticket_data[guild_id]["active_tickets"][str(ticket_channel.id)] = {
            "user_id": interaction.user.id,
            "ticket_number": ticket_number,
            "created_at": discord.utils.utcnow().isoformat()
        }
        self.save_ticket_data()

    @app_commands.command()
    async def closeticket(self, interaction: discord.Interaction):
        """Close a ticket"""
        guild_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)

        if (guild_id not in self.ticket_data or 
            channel_id not in self.ticket_data[guild_id]["active_tickets"]):
            return await interaction.response.send_message("This is not a ticket channel!", ephemeral=True)

        ticket_info = self.ticket_data[guild_id]["active_tickets"][channel_id]
        
        # Create transcript
        messages = []
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            messages.append(f"{message.author}: {message.content}")

        transcript = "\n".join(messages)
        
        # Create transcript file
        with open(f"ticket-{ticket_info['ticket_number']}-transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript)
        
        # Create file object from the saved transcript
        transcript_file = discord.File(
            f"ticket-{ticket_info['ticket_number']}-transcript.txt",
            filename=f"ticket-{ticket_info['ticket_number']}-transcript.txt"
        )

        # Send transcript to user
        user = interaction.guild.get_member(ticket_info["user_id"])
        if user:
            try:
                await user.send(
                    f"Your ticket #{ticket_info['ticket_number']} has been closed.",
                    file=transcript_file
                )
            except:
                pass

        # Delete channel after confirmation
        await interaction.response.send_message("Closing ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except discord.Forbidden:
            await interaction.followup.send("Failed to delete channel - missing permissions", ephemeral=True)
            return
        except discord.NotFound:
            pass  # Channel already deleted
        
        # Remove from active tickets
        del self.ticket_data[guild_id]["active_tickets"][channel_id]
        self.save_ticket_data()

        # Clean up transcript file
        try:
            os.remove(f"ticket-{ticket_info['ticket_number']}-transcript.txt")
        except:
            pass

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def addticketadmin(self, interaction: discord.Interaction, member: discord.Member):
        """Add a member to ticket support role"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.ticket_data:
            return await interaction.response.send_message("Ticket system not set up!", ephemeral=True)

        support_role = interaction.guild.get_role(self.ticket_data[guild_id]["support_role_id"])
        await member.add_roles(support_role)
        await interaction.response.send_message(f"Added {member.mention} to ticket support team")

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketstats(self, interaction: discord.Interaction):
        """View ticket statistics"""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.ticket_data:
            return await interaction.response.send_message("Ticket system not set up!", ephemeral=True)

        stats = self.ticket_data[guild_id]
        embed = discord.Embed(title="Ticket Statistics", color=discord.Color.blue())
        embed.add_field(name="Total Tickets Created", value=stats["ticket_counter"])
        embed.add_field(name="Active Tickets", value=len(stats["active_tickets"]))
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
