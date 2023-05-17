import discord
from discord.ext import commands
from discord import (
    app_commands,
)

import inflect
import itertools

from typing import Optional
from datetime import datetime

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                'cooldown': commands.CooldownMapping.from_cooldown(1, 5.0, commands.BucketType.user)
            }
        )

    def get_cooldown_signature(self, command: commands.Command):
        fmt = ""
        parent = command.full_parent_name
        if len(command.aliases):
            aliases = "|".join(command.aliases)
            if parent:
                fmt = f"{self.clean_prefix}{parent} [{command.name}|{aliases}]"
            else:
                fmt = f"{self.clean_prefix}{command.name} [{aliases}]"
        else:
            fmt = f"{self.clean_prefix}{command.name}" if not parent else f"{parent} {command.name}"
        return f"{fmt} {command.signature}"

    async def send_bot_help(self, mapping):
        bot = self.context.bot

        def key(command):
            return command.qualified_name

        fmt: list[commands.Command] = await self.filter_commands(bot.commands, sort=True, key=key)
        commands: dict[commands.Cog, list[commands.Command]] = {}

        for cog, command in itertools.groupby(fmt, key=key):
            cog = bot.get_cog(cog)
            commands[cog] = sorted(command, key=lambda c: c.qualified_name)

class Information(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.launch_time = self.bot.launch_time
        self._log = self.bot.logger

    @commands.hybrid_command()
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! Latency is `{0}ms`.".format(round(self.bot.latency * 1000)))

    @commands.hybrid_group()
    async def info(self, ctx: commands.Context):
        pass

    @info.command(name='server', description="Shows information about the server you are running the command in.")
    async def serverinfo(self, interaction: discord.Interaction):
        p = inflect.engine()
        created_at = interaction.guild.created_at
        date = datetime.strftime(created_at, "%a, "+p.ordinal("%d")+" %b, %Y %I:%M %p")    
        e = discord.Embed(
            color=discord.Color.blue(),
            timestamp = interaction.created_at
        )
        e.set_author(name=f"{interaction.guild}", icon_url=f"{interaction.guild.icon}")
        e.set_footer(text=f"Requested by {interaction.user}", icon_url=f"{interaction.user.avatar}")
        e.add_field(name="Server ID", value=f"{interaction.guild.id}")
        e.add_field(name="Owner", value=f"{interaction.guild.owner}")
        e.add_field(name="Members", value=f"{interaction.guild.member_count}")
        e.add_field(name="Categories", value=f"{categories}")   
        e.add_field(name="Text Channels", value=f"{len(interaction.guild.text_channels)}")
        e.add_field(name="Voice Channels", value=f"{len(interaction.guild.voice_channels)}")
        e.add_field(name="Created", value=f"{date}")
        e.add_field(name="Boosts" ,value=f"{interaction.guild.premium_subscription_count}")
        e.add_field(name="Boost Level", value=f"{interaction.guild.premium_tier}")
        e.add_field(name="Roles", value=f"{len(interaction.guild.roles)}")
        e.add_field(name="Emojis", value=f"{len(interaction.guild.emojis)}")
        e.add_field(name="Stickers", value=f"{len(interaction.guild.stickers)}")
        await interaction.response.send_message(embed=e)

    @info.command(name="user", description="Shows information about a user. If no user is provided, it shows your info.")
    @app_commands.describe(user="The user to get the information of.")
    async def userinfo(self, interaction: discord.Interaction, user: Optional[discord.Member]):
        member = interaction.guild.get_member(interaction.user.id) if user is None else interaction.guild.get_member(user.id)
        if str(member.raw_status) == "online":
            status = ":green_circle: Online"
        elif str(member.raw_status) == "dnd":
            status = ":no_entry: Do Not Disturb"    
        elif str(member.raw_status) == "offline":
            status = ":black_circle: Offline"
        elif str(member.raw_status) == "idle":
            status = ":crescent_moon: Idle"
        rolelist = [role.mention for role in member.roles if role != interaction.guild.default_role]
        roles = (", ".join(rolelist))
        p = inflect.engine()
        joined_at = datetime.strftime(member.joined_at, "%a, "+p.ordinal("%d")+" %b, %Y %I:%M %p") 
        created_at = datetime.strftime(member.created_at, "%a, "+p.ordinal("%d")+" %b, %Y %I:%M %p")            
        permissionlist = []
        for name, value in member.guild_permissions:
            if value:
                permissionlist.append(name)
        permissions = ", ".join(permissionlist).replace("_", " ").title()            
        e = discord.Embed(
            color=discord.Color.blue(),
            timestamp = interaction.created_at
        )
        e.set_author(name=f"{member}", icon_url=f"{member.avatar}")
        e.set_footer(text=f"ID: {member.id}")
        e.add_field(name="Nickname", value=f"{member.nick}")
        e.add_field(name="Account Type", value="Bot" if member.bot else "Human")
        e.add_field(name="Status", value=status)
        e.add_field(name="Joined", value=f"{joined_at}")
        e.add_field(name="Registered", value=f"{created_at}")
        e.add_field(name="Roles", value=f"{roles}", inline=False)
        e.add_field(name="Permissions", value=f"{permissions}", inline=False)
        await interaction.response.send_message(embed=e)

    @info.command(name="role", description="Shows information about a role.")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        rolelist = [name.mention for name in role.members]
        roles = (", ".join(rolelist))
        p = inflect.engine()
        created_at = datetime.strftime(role.created_at, p.ordinal("%d")+" %B, %Y")
        embedRoleInfo = discord.Embed(
            description=f"Information about {role.mention}:",
            color=discord.Color.blue(),
            timestamp = interaction.created_at
        )
        e.set_author(name=f"{interaction.guild.name}", icon_url=f"{interaction.guild.avatar}")
        e.set_footer(text=f"Requested by {interaction.user}", icon_url=f"{interaction.user.avatar}")
        e.add_field(name="Role ID", value=f"{role.id}")
        e.add_field(name="Hoisted", value=f"{role.hoist}")
        e.add_field(name="Color", value=f"{role.color}")
        e.add_field(name="Mentionable", value=f"{role.mentionable}")
        e.add_field(name="Position", value=f"{role.position}")
        e.add_field(name="Created", value=f"{created_at}")
        e.add_field(name="Members", value=[roles if roles is not [''] else "No members have this role."], inline=False)
        await interaction.response.send_message(embed=e)

    @info.command(name="uptime", description="Shows the bot's uptime.")
    async def uptime(self, interaction: discord.Interaction):
        uptime = datetime.utcnow() - self.launch_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        e = discord.Embed(
            description=f"I have been up for `{days}` days, `{hours}` hours, `{minutes}` minutes and `{seconds}` seconds.",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        await interaction.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(Information(bot))