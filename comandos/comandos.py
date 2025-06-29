import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from typing import Final
import asyncpg

load_dotenv()
DB_URL: Final[str] = os.getenv("DB_URL")

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="p")
    async def perfil(self, ctx):
        user = ctx.author
        user_id = user.id

        db_con = await asyncpg.connect()

        result = await db_con.fetchrow("SELECT karma FROM usuario WHERE id = $1", user_id)
        await db_con.close()

        karma = result["karma"] if result else 0

        embed = discord.Embed(
            title=f"👤 Perfil de {user.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.add_field(name="Karma", value=f"🌀 {karma}", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Perfil(bot))