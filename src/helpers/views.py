import discord

from helpers import (
    Requests,
    ApexContext
)

class UrbanDefine(discord.ui.View):
    def __init__(
        self,
        ctx: ApexContext,
        data: dict,
        pages: int,
        word: str
    ):
        super().__init__(timeout=60.0)

        self.data: dict = data
        self.ctx: ApexContext = ctx
        self.message: discord.Message = None
        self.pages: int = pages
        self.current: int = 0
        self.word: str = word

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            return True

        await interaction.response.send_message("This is not your define menu.", ephemeral=True)
        return False

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(viwe=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.grey)
    async def backward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = 0

        definition = self.data['list'][0]['definition'].replace("[", "").replace("]", "")
        upvotes = self.data['list'][0]['thumbs_up']
        downvotes = self.data['list'][0]['thumbs_down']
        author = self.data['list'][0]['author']
        examples = self.data['list'][0]['example'].replace("[", "").replace("]", "")

        button.disabled = True
        self.back.disabled = True

        e = discord.Embed(
            title=f"Definition of {self.word}",
            description=f"**Definition**:\n{definition}\n**Author**:\n{author}\n**Examples**:\n{examples}\n**Votes**:\nUpvotes: {upvotes}\nDownvotes: {downvotes}",
            color=discord.Color.blue(),
            timestamp=self.message.created_at
        )
        e.set_footer(text="Page 1/10")
        await interaction.response.edit_message(embed=e, view=self)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.grey)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current -= 1

        definition = self.data['list'][self.current]['definition'].replace("[", "").replace("]", "")
        upvotes = self.data['list'][self.current]['thumbs_up']
        downvotes = self.data['list'][self.current]['thumbs_down']
        author = self.data['list'][self.current]['author']
        examples = self.data['list'][self.current]['example'].replace("[", "").replace("]", "")

        if self.current == 0:
            button.disabled = True
            self.backward.disabled = True
        
        if self.current > 0 and self.current < 9:
            for item in self.children:
                item.disabled = False

        e = discord.Embed(
            title=f"Definition of {self.word}",
            description=f"**Definition**:\n{definition}\n**Author**:\n{author}\n**Examples**:\n{examples}\n**Votes**:\nUpvotes: {upvotes}\nDownvotes: {downvotes}",
            color=discord.Color.blue(),
            timestamp=self.message.created_at
        )
        e.set_footer(text=f"Page {self.current+1}/10")

        await interaction.response.edit_message(embed=e, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1

        definition = self.data['list'][self.current]['definition'].replace("[", "").replace("]", "")
        upvotes = self.data['list'][self.current]['thumbs_up']
        downvotes = self.data['list'][self.current]['thumbs_down']
        author = self.data['list'][self.current]['author']
        examples = self.data['list'][self.current]['example'].replace("[", "").replace("]", "")

        if self.current == 9:
            button.disabled = True
            self.forward.disabled = True

        if self.current > 0 and self.current < 9:
            for item in self.children:
                item.disabled = False

        e = discord.Embed(
            title=f"Definition of {self.word}",
            description=f"**Definition**:\n{definition}\n**Author**:\n{author}\n**Examples**:\n{examples}\n**Votes**:\nUpvotes: {upvotes}\nDownvotes: {downvotes}",
            color=discord.Color.blue(),
            timestamp=self.message.created_at
        )
        e.set_footer(text=f"Page {self.current+1}/10")

        await interaction.response.edit_message(embed=e, view=self)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.grey)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = 9

        definition = self.data['list'][self.current]['definition'].replace("[", "").replace("]", "")
        upvotes = self.data['list'][self.current]['thumbs_up']
        downvotes = self.data['list'][self.current]['thumbs_down']
        author = self.data['list'][self.current]['author']
        examples = self.data['list'][self.current]['example'].replace("[", "").replace("]", "")

        self.next.disabled = True
        button.disabled = True

        e = discord.Embed(
            title=f"Definition of {self.word}",
            description=f"**Definition**:\n{definition}\n**Author**:\n{author}\n**Examples**:\n{examples}\n**Votes**:\nUpvotes: {upvotes}\nDownvotes: {downvotes}",
            color=discord.Color.blue(),
            timestamp=self.message.created_at
        )
        e.set_footer(text="Page 10/10")

        await interaction.response.edit_message(embed=e, view=self)

    @discord.ui.button(label="End Interaction", style=discord.ButtonStyle.red)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(view=self)



