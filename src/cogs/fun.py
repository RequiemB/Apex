import discord
from discord.ext import commands
from discord import (
    app_commands,
    SelectOption,
    TextStyle
)
from discord.ui import (
    Modal,
    TextInput,
    View,
    Button,
    Select
)

import aiohttp
import asyncio
import re
import traceback
import asqlite
import logging

from datetime import datetime
from babel import Locale
from helpers import (
    ApexContext,
    Requests,
    views
)

regex = ("((http|https)://)(www.)?[a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)")

class Translator(Modal, title="Apex Translator"):
    text = TextInput(label="Text", placeholder="Enter the text you want to translate here...", style=TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        translate = getattr(Fun, "_translate")
        self._translation = translate(interaction.locale, self.text.value)
        translation = self._translation[0]['translations'][0]['text']
        language = Locale(self._translation[0]['detectedLanguage']['language']).display_name
        target_language = Locale(str(interaction.locale)[0:2]).display_name
        if language == target_language:
            return await interaction.followup.send(f"The message you tried to translate is already in {language}.")
        e = discord.Embed(
            title = "Translation",
            description = f"Translation of ID `{id}` was **successful**.",
            color = discord.Color.blue(),
            timestamp = datetime.utcnow()
        )
        e.add_field(name="Detected Language", value=str(language))
        e.add_field(name="Target Language", value=str(target_language))
        e.add_field(name="From", value=self.text.value, inline=False)
        e.add_field(name="To", value=translation)
        e.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar is not None else None)
        await interaction.response.send_message(embed=e)

    async def on_error(self, interaction: discord.Interaction, error):
        if isinstance(error, aiohttp.ClientPayloadError):
            await interaction.response.send_message("I can\'t translate this message. It's too long.")

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.translation = None
        self.driver = None
        self.url = re.compile(regex)
        self._http = self.bot._http
        self._log: logging.Logger = bot.logger
        self.context_menu = app_commands.ContextMenu(
            name = "Translate",
            callback = self._context_translate,
        )
        self.context_menu.guild_only = True
        self.bot.tree.add_command(self.context_menu)
        self.translations = 0
        self._requests = Requests(bot)

    async def cog_unload(self) -> None:
        self.driver.close()
        self._log.debug("Closed firefox session.")

    async def is_url_valid(self, url: str):
        return re.search(self.url, url)

    async def _translate(self, locale, text):
        query= {"api-version":"3.0","to[0]":locale,"textType":"plain","profanityAction":"NoAction"}

        payload = [{"Text": str(text)}]
        headers = {
        	"content-type": "application/json",
        	"X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com",
        	"X-RapidAPI-Key": config.RAPIDAI_API_KEY
        }
        resp = await self._http.post("https://microsoft-translator-text.p.rapidapi.com/translate", params=query, headers=headers, json=payload)
        data = await resp.json()
        return data

    async def _context_translate(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            self._translation = await self._translate(interaction.locale, message.content)
        except aiohttp.ClientPayloadError:
            await interaction.followup.send("I can\'t translate this message. It's too long.")
        else:
            translation = self._translation[0]['translations'][0]['text']
            language = Locale(self._translation[0]['detectedLanguage']['language']).display_name
            target_language = Locale(str(interaction.locale)[0:2]).display_name
            if language == target_language:
                return await interaction.followup.send(f"The message you tried to translate is already in {language}.")
            await interaction.followup.send("{0} -> {1}: {2}".format(str(language), str(target_language), translation))
            self.translations += 1

    @commands.hybrid_command(description="Shows the screenshot of a website.")
    @app_commands.describe(url="The URL of the website.")
    async def website(self, ctx: ApexContext, url: str):
        if not await self.is_url_valid(url):
            return await ctx.send("The URL you provided was an invalid one. Try again. The URL: {0}".format(url), ephemeral=True)
        try:
            self.driver.get(url)
        except Exception:
            traceback.print_exc()
            await ctx.send("""An error occured while connecting to <{0}>. It may be one of the errors below.
            > The URL doesn't exist.
            > The website is down at the moment.
            > The website may promote NSFW content.
            > The page you are trying to view cannot be shown because the authenticity of the received data could not be verified.
            > The browser is not responding.""".format(url), ephemeral=True)
        else:
            await ctx.defer(thinking=True)
            await asyncio.sleep(1)
            self.driver.get_screenshot_as_file("website.png")
            screenshot = discord.File("website.png", "website.png")
            await ctx.send(file=screenshot)

    @commands.hybrid_command(description="A normal translator.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def translate(self, ctx: ApexContext):
        if ctx.interaction is None:
            e = discord.Embed(description="reaction This command can only be used as a slash command due to Discord limitations.")
            return await ctx.send(embed=e)
        await ctx.send(Translator())

    @commands.hybrid_command(description="Looks up the word on the Urban Dictionary and returns all the definitions available.")
    @app_commands.describe(word="The word you want to get the definition of.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def define(self, ctx: ApexContext, *, word: str):
        message = await ctx.send(f"Getting information about the word `{word}`, please wait a few seconds.")
        data = await self._requests.get_definition(word)

        assert data

        try:
            pages = 0
            for i in data['list']:
                pages += 1


            definition = data['list'][0]['definition'].replace("[", "").replace("]", "")
            upvotes = data['list'][0]['thumbs_up']
            downvotes = data['list'][0]['thumbs_down']
            author = data['list'][0]['author']
            examples = data['list'][0]['example'].replace("[", "").replace("]", "")

            view = views.UrbanDefine(ctx, data, pages, word)

            view.backward.disabled = True
            view.back.disabled = True

            e = discord.Embed(
                title=f"Definition of {word}",
                description=f"**Definition**:\n{definition}\n**Author**:\n{author}\n**Examples**:\n{examples}\n**Votes**:\nUpvotes: {upvotes}\nDownvotes: {downvotes}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            e.set_footer(text=f"Page 1/{pages}")
            view.message = await message.edit(content=None, embed=e, view=view)
            if view.message is None:
                view.message = await ctx.interaction.original_response()

        except KeyError:
            e = discord.Embed(
                description=f"No word named {word} found.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=e)
        except Exception as e:
            e = discord.Embed(
                description=f"An error occured, if it still occurs, report it using `/bugreport`.\n\nError Info: `{e.__class__.__name__}: {e}.`",
                color=discord.Color.red()
            )
            return await ctx.send(embed=e)

    @commands.hybrid_command(description="Starts an interactive Trivia session with the bot.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def trivia(self, ctx: ApexContext):
        pass
    
async def setup(bot):
    await bot.add_cog(Fun(bot))

