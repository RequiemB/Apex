import discord
from discord.ext import commands
from discord import app_commands

from discord import NotFound
from discord.ext.commands.errors import (BadArgument, BadUnionArgument,
                                         ChannelNotFound, CommandOnCooldown,
                                         MemberNotFound,
                                         MissingRequiredArgument, NotOwner,
                                         RoleNotFound, UserNotFound)

async def on_command_error(ctx: commands.Context, error):
    if hasattr(ctx.command, 'on_error'):
        return

    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    ignored = (commands.CommandNotFound)

    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return

    if isinstance(error, ChannelNotFound):
        e = discord.Embed(description= "<:reactionFailure:983059904979959819>" f" Channel was not found.", color=discord.Color.red())        
        return await ctx.send(embed=e)
    elif isinstance(error, MemberNotFound) or isinstance(error, UserNotFound):
        e = discord.Embed(description= "<:reactionFailure:983059904979959819>" f" User/Member was not found.", color=discord.Color.red())        
        return await ctx.send(embed=e)
    elif isinstance(error, RoleNotFound):
        e = discord.Embed(description= "<:reactionFailure:983059904979959819>" f" Role was not found.", color=discord.Color.red())        
        return await ctx.send(embed=e)
    elif isinstance(error, MissingRequiredArgument) or isinstance(error, BadArgument):
        e = discord.Embed(description="<:reactionFailure:983059904979959819>" f" Correct usage of the command: {ctx.command.name} {ctx.command.signature}", timestamp=ctx.message.created_at, color=discord.Color.red())
        e.set_footer(text="[] means the argument is optional and <> means the argument is required.")
        return await ctx.send(embed=e)
    elif isinstance(error, NotOwner):
        owners = []
        for owner in self.bot.owner_ids:
            owners.append(self.bot.get_user(owner).mention)
        owner = " & ".join(owners)
        e = discord.Embed(description=f"<:reactionFailure:983059904979959819> Only the bot owners ({owner}) can use this command/module.", color=discord.Color.red())
        return await ctx.send(embed=e)
    elif isinstance(error, BadUnionArgument):
        e = discord.Embed(
            title = "BadUnionArgument",
            description = "An exception occured that inherits from `BadUnionArgument`.",
            color = discord.Color.red(),
            timestamp = ctx.message.created_at
        )
        e.add_field(name="Parameter/Argument", value=error.param)
        e.add_field(name="Converters", value=error.converters)
        e.add_field(name="Errors", value=", ".join(error.errors))
        e.set_footer(text=f"Command invoked by {ctx.author}", icon_url=ctx.author.avatar.url)
        return await ctx.send(embed=e)
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if interaction.command is None or hasattr(interaction.command, "error"):
            return

    if hasattr(interaction.command.cog, "on_app_command_error"):
        func = getattr(interaction.command.cog, "on_app_command_error")
        await func(interaction, error)
    else:
        pass