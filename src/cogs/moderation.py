import discord
from discord.ext import (
    tasks,
    commands
)
from discord.ui import (
    View,
    Button,
    Select
)
from discord import (
    app_commands,
    utils
)

import asyncio
import traceback
import logging

from datetime import datetime
from typing import (
    Optional,
    Literal
)
from helpers import (
    ApexContext
)

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._log: logging.Logger = bot.logger

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            e = discord.Embed(description = ":arrows_counterclockwise: This command is currently on cooldown. You can use it after {0} seconds.".format(str(error.retry_after)[0:3]), color = discord.Color.red())
            await ctx.send(embed=e)
        if isinstance(error, app_commands.MissingPermissions):
            permissions = ", ".join(error.missing_permissions).replace("_", " ").title()
            e = discord.Embed(description = "<:reactionFailure:903828621989412884> You require the **{0}** permissions to run this command.".format(permissions), color = discord.Color.red())
            await ctx.send(embed=e)
        if isinstance(error, app_commands.BotMissingPermissions):
            permisisons = ", ".join(error.missing_permissions).replace("_", " ").title()
            e = discord.Embed(description = "<:reactionFailure:903828621989412884> I require the **{0}** permissions to run this command.".format(permissions), color = discord.Color.red())
            await ctx.send(embed=e)
        else:
            raise error

    @commands.hybrid_command(name="kick", description="Kicks a user from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(member="The member to kick.", reason="The reason for kicking the member. Can be None.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def kick(
        self, 
        ctx: ApexContext, 
        member: discord.Member, 
        *, 
        reason: Optional[str]
    ):
        if member == ctx.guild.me:
            return await ctx.send("I can't kick myself.", ephemeral=True)
        if member.guild_permissions.administrator:
            e = discord.Embed(description= "<:reactionFailure:903828621989412884> I can't kick an administrator.", color=discord.Color.red())                   
            return await ctx.send(embed=e)
        if ctx.guild.me.top_role.position <= member.top_role.position:
            e = discord.Embed(
                description = "<:reactionFailure:903828621989412884> My role is not high enough to peform moderation actions on {0}. Move my role above {1}.".format(member.mention, member.top_role.mention),
                color = discord.Color.red()
            )
            return await ctx.send(embed=e)
        try:
            await member.kick(reason = "Done by {0}. Reason: {1}".format(ctx.user, "No reason provided." if reason is None else reason))
        except discord.HTTPException as h:
            self._log.warning("An HTTPException occured while executing the kick command. Information about the exception: {0} {1} {2}".format(e.text, e.status, e.code))
            e = discord.Embed(
                title = "HTTPException",
                description = "An HTTPException occured while kicking this user. The details of the exception has been provided below.\nIt may be due to a Discord API Outage. Try running the command again.",
                color = discord.Color.red(),
                timestamp = ctx.created_at
            )
            e.add_field(name = "Message", value = h.text)
            e.add_field(name = "Status Code", value = h.status)
            e.add_field(name = "Discord Error Code", value = h.code)
            e.set_footer(text = "We're really sorry for the inconvenience.")
            return await ctx.send(embed=e, ephemeral=True)
        e = discord.Embed(
            title = "Command Information",
            description = "**{0}** was kicked from the server.".format(member),
            timestamp = ctx.created_at,
            color = discord.Color.blue()
        )
        e.add_field(name = "By", value = ctx.user.mention)
        e.add_field(name = "Reason", value = "No reason provided." if reason is None else reason)
        e.add_field(name = "Relative Time", value = utils.format_dt(datetime.now(), style = "R"))
        e.set_footer(text = "For support and to report bugs, make sure to join my support server.")
        await ctx.send(embed=e)

    @app_commands.command(name = "purge", description = "Removes a number of messages from the channel specified.")
    @app_commands.describe(amount = "Number of messages to remove. If you aren't an administrator, you can only remove up to 25 messages at once.")
    @app_commands.describe(channel = "Channel to remove the messages from. Defaults to the channel the command is being invoked.")
    @app_commands.describe(member = "The member to delete the messages of.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    @app_commands.checks.cooldown(1, 7.0, key=lambda i: i.user.id)
    async def purge(
        self, 
        ctx: ApexContext, 
        amount: int, 
        channel: Optional[discord.TextChannel], 
        member: Optional[discord.Member]
    ):
        amount = 25 if amount > 25 and not ctx.user.guild_permissions.administrator else amount
        channel = ctx.channel if channel is None else channel
        def is_user(m):
            return m.author == member
        try:
            if member is not None:
                await channel.purge(limit=amount, check=is_user)
            else:
                await channel.purge(limit=amount)
        except discord.HTTPException as h:
            self._log.warning("An HTTPException occured while executing the purge command. Information about the exception: {0} {1} {2}".format(e.text, e.status, e.code))
            e = discord.Embed(
                title = "HTTPException",
                description = "An HTTPException occured while purging messages. The details of the exception has been provided below.\nIt may be due to a Discord API Outage. Try running the command again.",
                color = discord.Color.red(),
                timestamp = ctx.created_at
            )
            e.add_field(name = "Message", value = h.text)
            e.add_field(name = "Status Code", value = h.status)
            e.add_field(name = "Discord Error Code", value = h.code)
            e.set_footer(text = "We're really sorry for the inconvenience.")
            return await ctx.send(embed=e, ephemeral=True)
        e = discord.Embed(description = "<:reactionSuccess:903931128493264926> Deleted {0} messages from {1}.".format(amount, channel.mention), color = discord.Color.blue())
        await ctx.send(embed=e) if ctx.channel != channel else await ctx.send(embed=e, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))