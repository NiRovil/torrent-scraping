import discord
from bot_resources import Resources

from image_scrap import Image
from torrent_scrap import *

stock_img = 'https://media.istockphoto.com/id/1159854564/pt/vetorial/pirate-skull-emblem-illustration-with-crossed-sabers.jpg?s=612x612&w=is&k=20&c=nxDfMkuCWG5ZreLbNN9xqEMZM0XEqDPPpIMnzzvxlws='

class Bot(discord.Client):

    # Everything is alright? We need it!
    # Send a confirmation in terminal if everything is set up.
    async def on_ready(self): await self.ready()

    # Send the final message for the user.
    async def on_message(self, message): await self.download_result(message)

    @staticmethod
    def embed_message(torrents: list, query: str):
        """
            Creation of the final embed message sent on discord.
        """

        # Define a title for the embed message.
        title = f'RESULTADOS PARA {query.upper()}'
        embed = discord.Embed(title=title)
        null_result = ['Nada encontrado!', 'Tente outro termo!']

        if torrents:
            # Scrap an image cover of the game, if not found, a stock one is used.
            try:
                embed.set_thumbnail(url=Image(query))
            except: 
                embed.set_thumbnail(url=stock_img)

        # For each torrent link in the top 5, create an embed link.
        for torrent in torrents:
            _title = f'Name: {torrent[1]} | Space: {torrent[3]} | Seeds: {torrent[4]} | Release: {torrent[5]}'
            _download = ScrapDownload(torrent[6])
            _magnet = ScrapMagnet(torrent[6])
            _short_link = Resources.mgnetme(_magnet)
            _link = f"[Download]({_download}) | [Link Direto]({_short_link})"

            embed.add_field(name=_title, value=_link, inline=False)

            return embed
        
        embed.set_thumbnail(url=stock_img)
        embed.add_field(name=null_result[0], value=null_result[1], inline=False)

        return embed

    @staticmethod
    def torrent_request(message):
        """
            Bot trigger!
        """
        content = message.content

        # Difine the keywords used to trigger the bot.
        for keyword in ['!torrent', '!t']:
            if content.startswith(keyword + ' ') and len(content) > len(keyword + ' '):
                return True
            
        return False

    @staticmethod
    def query_search(message):
        """
            Retrieve the query used during bot trigger.
        """
        content = message.content
        filtered = content.split(' ')
        return ' '.join(filtered[1:])

    async def discord_response_query(self, message,query):
        """
            Start scraping torrents.
        """
        scrap = ScrapSearch(query)
        torrents = []
        for torrent in scrap():
            torrents.append(torrent)

        embed = self.embed_message(torrents=torrents, query=query)
        return embed

        return ''

    async def download_result(self, message):
        """
            Send the final message to the user.
        """

        # Check if everything is alright with the user query.
        if self.torrent_request(message):
            query = self.query_search(message)

            try:
                embed = await self.discord_response_query(message=message, query=query)
                await message.channel.send(embed=embed)

            except:
                await message.channel.send('Algo deu errado na sua busca ):')

    async def ready(self):
        print('Logged in!')

# Launch the bot.
import os
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    intents = discord.Intents.default()
    intents.message_content = True
    client = Bot(intents=intents)
    client.run(os.getenv('API_KEY'))