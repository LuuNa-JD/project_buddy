import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logging.debug("Bot is starting...")
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.members = True
intents.typing = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def main():
    async with bot:
        await bot.load_extension('client_management')
        await bot.load_extension('news_scraper')
        await bot.start(DISCORD_TOKEN)

# Démarrer le bot
asyncio.run(main())
