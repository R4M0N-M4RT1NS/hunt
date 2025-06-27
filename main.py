import os
import sys
import discord
from discord.ext import commands
from typing import Final
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("TOKEN está vazio, tente novamente com o TOKEN inserido corretamente")
    sys.exit(401)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="-", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"A caçada começou! {bot.user}")

    await bot.load_extension("eventos.eventos")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await bot.process_commands(message)

async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
