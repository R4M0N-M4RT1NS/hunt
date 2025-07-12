import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import eventos.eventos as event
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("TOKEN está vazio")
    sys.exit(401)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=";", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    await event.register(member)

@bot.event
async def on_ban(guild, user):
    await event.register_ban(user.id)

async def main():
    async with bot:
        await bot.load_extension("comandos.comandos")
        # await bot.load_extension("interacao.encontros")
        print("✅ Comandos e Eventos carregados")
        await bot.start(TOKEN)

asyncio.run(main())
