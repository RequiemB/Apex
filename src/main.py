import discord
from discord.ext import commands
from discord import app_commands

import asyncio
import os
import logging
import traceback
import aiohttp

from helpers import (
    config,
    logs,
    handlers
)
from datetime import datetime
from dotenv import load_dotenv
from pkgutil import iter_modules

_log = logging.getLogger("discord")
_log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logs.Logger())
_log.addHandler(ch)

class Apex(commands.Bot):
    def __init__(self):

        self._activity_text = config.ACTIVITY_TEXT
        self._activity_type = getattr(discord.ActivityType, config.ACTIVITY_TYPE)

        if len(self._activity_text) == 0:
            self._activity_text = "over your guild."

        if self._activity_type is None:
            self._activity_type = discord.ActivityType.watching

        super().__init__(
            command_prefix=self._get_prefix,
            intents = discord.Intents.all(), 
            status=discord.Status.dnd, 
            activity=discord.Activity(name=self._activity_text, type=self._activity_type),
            owner_ids=config.OWNER_IDS
        )
        self._extensions = [m.name for m in iter_modules(['cogs'], prefix='cogs.')]
        self.tree.on_error = self.on_app_command_error

    def _get_prefix(self, bot: commands.Bot, message: discord.Message):
        return config.PREFIXES

    async def setup_hook(self) -> None:
        os.system("clear")
        self._http = aiohttp.ClientSession()
        self.launch_time = datetime.utcnow()
        self.logger = _log
        for extension in self._extensions:
            try:
                await self.load_extension(extension)
            except:
                _log.error(f"An error occured while loading extension {extension}")
                traceback.print_exc()
            else:
                _log.info("Loaded {0}.".format(extension))

    async def close(self):
        await self._http.close()
        _log.info("Closed aiohttp session.")

        await super().close()
    
    async def on_ready(self):
        self.logger.info("Logged in as ", self.user)

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        handler = getattr(handlers, "on_app_command_error")
        if handler:
            await handler(ctx, error)
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        handler = getattr(handlers, "on_command_error")
        if handler:
            await handler(ctx, error)

bot = Apex()

async def main():
    async with bot:
        load_dotenv()
        await bot.start(os.getenv("TOKEN"))
        
asyncio.run(main())

        
