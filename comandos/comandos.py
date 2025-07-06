import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from typing import Final
import asyncpg
import re

load_dotenv()
DB_URL: Final[str] = os.getenv("DB_URL")

class Faces(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="p")
    async def perfil(self, ctx):
        user = ctx.author
        user_id = user.id

        db_con = await asyncpg.connect(DB_URL)
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

class FormularioModal(discord.ui.Modal, title="Criar Canal de Voz"):
    nome = discord.ui.TextInput(label="Nome do Canal", placeholder="Ex: Festinha dos Recrutas")
    tamanho = discord.ui.TextInput(label="Tamanho Máximo", placeholder="Ex: 5", max_length=2)
    whitelist = discord.ui.TextInput(
        label="Mencione os usuários permitidos (@usuário)",
        style=discord.TextStyle.paragraph,
        placeholder="@fulano @ciclano"
    )

    def __init__(self, cog, autor):
        super().__init__()
        self.cog = cog
        self.autor = autor

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, name="Canais de Voz")
        if not categoria:
            categoria = await guild.create_category("Canais de Voz")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=True),
            self.autor: discord.PermissionOverwrite(manage_channels=True)
        }

        canal = await guild.create_voice_channel(
            name=self.nome.value,
            user_limit=int(self.tamanho.value),
            overwrites=overwrites,
            category=categoria
        )

        ids = [int(u_id) for u_id in re.findall(r"\\d+", self.whitelist.value)]

        self.cog.canais_monitorados[canal.id] = {
            "canal": canal,
            "empty_since": None,
            "whitelist": ids
        }

        await interaction.response.send_message(f"🔊 Canal `{canal.name}` criado com sucesso!", ephemeral=True)

class FormularioBotao(discord.ui.View):
    def __init__(self, cog, autor):
        super().__init__(timeout=60)
        self.cog = cog
        self.autor = autor

    @discord.ui.button(label="Formulário", style=discord.ButtonStyle.blurple)
    async def abrir_formulario(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FormularioModal(self.cog, self.autor))

class VoiceControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.canais_monitorados = {}  # canal_id: { canal, whitelist, empty_since }
        self.monitorar_canais.start()

    @commands.command(name="c")
    async def abrir_criador(self, ctx):
        await ctx.send("Clique no botão e preencha o formulário", view=FormularioBotao(self, ctx.author))

    @tasks.loop(seconds=5)
    async def monitorar_canais(self):
        now = discord.utils.utcnow()

        for cid, info in list(self.canais_monitorados.items()):
            canal = info["canal"]
            membros = canal.members
            whitelist = info["whitelist"]

            if not membros:
                if info["empty_since"] is None:
                    info["empty_since"] = now
                elif (now - info["empty_since"]).total_seconds() > 15:
                    try:
                        await canal.delete()
                    except Exception:
                        pass
                    del self.canais_monitorados[cid]
            else:
                info["empty_since"] = None
                for m in membros:
                    if m.bot:
                        continue
                    try:
                        await m.edit(mute=(m.id not in whitelist))
                    except discord.Forbidden:
                        pass

    def cog_unload(self):
        self.monitorar_canais.cancel()

async def setup(bot):
    print("✅ Cog de comandos carregado")
    await bot.add_cog(Faces(bot))
    await bot.add_cog(VoiceControl(bot))
