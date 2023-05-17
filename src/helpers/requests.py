import aiohttp

class Requests:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        
        # Urls

        self.urban_base_url = 'https://api.urbandictionary.com/v0/define'

    async def get_definition(self, query: str):
        extended_url = self.urban_base_url + f"?term={query}"

        resp = await self.session.get(extended_url)
        data = await resp.json()
        
        return data
