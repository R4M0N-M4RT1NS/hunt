import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from typing import Final
import asyncpg
import re

load_dotenv()
DB_URL: Final[str] = os.getenv("DB_URL")

## PARTE VOLTADA AO COMANDO DE AJUDA

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="I")
    async def instrucoes(self, ctx):
        embed = discord.Embed(
            title="✨ Tutorial do Bot",
            description="Bem-vindo ao bot **Caçada**! \nAqui estão os comandos que você pode usar:",
            color=discord.Color.green()
        )

        embed.add_field(
            name="😶 `;p` - Ver Perfil",
            value="Mostra seu perfil com o karma atual.",
            inline=False
        )

        embed.add_field(
            name="🎙️ `;c` - Criar Canal de Voz",
            value="Abre um botão para preencher um formulário e criar um canal de voz com nome, limite e uma whitelist de usuários.\n\nOs canais criados pelo comando são temporários\nUsuários fora da whitelist serão mutados ao entrarem no canal criado.\n`recomendo pegar os @'s antes de abrir o formulário.`",
            inline=False
        )

        # embed.add_field(
        #     name="📱 `;r` - Redes Sociais",
        #     value="Mostra os links das redes sociais do **Bar da Meia Noite**.",
        #     inline=False
        # )

        embed.set_footer(text="Caçada - Bot Oficial • Use com sabedoria.")

        await ctx.send(embed=embed)
## PARTE VOLTADA ÁS REDES SOCIAIS

class Redes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="r")
    async def instrucoes(self, ctx):
        embed = discord.Embed(
            title="✨ Redes Sociais",
            description="Aqui você encontra o **Bar da Meia Noite** nas redes sociais. Escolha uma abaixo:",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=RedesView())

class RedesView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(discord.ui.Button(
            label="  Instagram ",
            url="https://www.instagram.com/o.bar.da.meia.noite/",
            emoji="📸"
        ))
        self.add_item(discord.ui.Button(
            label="  Bluesky   ",
            url="https://bsky.app/profile/o-bar-da-meianoite.bsky.social",
            emoji="🌐"
        ))
        self.add_item(discord.ui.Button(
            label="  X / Twitter",
            url="https://x.com/OMeia20876",
            emoji="🐦"
        ))
        self.add_item(discord.ui.Button(
            label="  TikTok    ",
            url="https://www.tiktok.com/@obardameianoite?lang=pt-BR",
            emoji="🎵"
        ))

## PARTE VOLTADA AO PERFIL DO USUÁRIO

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

## PARTE VOLTADA AOS CANAIS DE VOZ

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

## PARTE VOLTADA AO SISTEMA DE BUGIGANGAS

class Bugigangas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="B")
    async def gerenciar_bugigangas(self, ctx):
        if not any(role.name == "Coçada" for role in ctx.author.roles):
            await ctx.send("Você não tem permissão para usar esse comando.")
            return

        view = BugigangaButton(self.bot, ctx.author)
        await ctx.send("Clique no botão abaixo para gerenciar bugigangas:", view=view)

class BugigangaForm(discord.ui.Modal, title="Gerenciar Bugigangas"):
    def __init__(self, bot, author):
        super().__init__()
        self.bot = bot
        self.author = author

        self.acao = discord.ui.TextInput(
            label="Ação (adicionar ou retirar)",
            placeholder="Adicionar ou Retirar",
            required=True
        )
        self.quantidade = discord.ui.TextInput(
            label="Quantidade",
            placeholder="Ex: 5",
            required=True
        )
        self.usuario = discord.ui.TextInput(
            label="ID do usuário de destino",
            placeholder="Botão direito e copie o ID",
            required=True
        )

        self.add_item(self.acao)
        self.add_item(self.quantidade)
        self.add_item(self.usuario)

    async def on_submit(self, interaction: discord.Interaction):
        canal_log = discord.utils.get(interaction.guild.text_channels, name="bugigangas")

        if not any(role.name == "Coçada" for role in interaction.user.roles):
            await interaction.response.send_message("Você não tem permissão para isso.", ephemeral=True)
            return

        acao = self.acao.value.lower()
        try:
            quantidade = int(self.quantidade.value)
            alvo_id = int(self.usuario.value)
        except ValueError:
            await interaction.response.send_message("Quantidade ou ID inválido.", ephemeral=True)
            return

        if acao not in ["adicionar", "retirar"]:
            await interaction.response.send_message("Ação inválida. Use 'adicionar' ou 'retirar'.", ephemeral=True)
            return

        if acao == "retirar":
            quantidade = -quantidade

        db_con = await asyncpg.connect(DB_URL)
        await db_con.execute(
            '''UPDATE usuario SET bugigangas = bugigangas + $1 WHERE id = $2''',
            quantidade, alvo_id
        )
        await db_con.close()

        user_mencionado = interaction.guild.get_member(alvo_id)
        texto_log = f"{interaction.user.mention} {'retirou' if acao == 'retirar' else 'adicionou'} {abs(quantidade)} bugiganga(s) de {user_mencionado.mention if user_mencionado else f'<@{alvo_id}>'}"
        if canal_log:
            await canal_log.send(texto_log)

        await interaction.response.send_message("✅ Ação registrada com sucesso.", ephemeral=True)

class BugigangaButton(discord.ui.View):
    def __init__(self, bot, author):
        super().__init__(timeout=60)
        self.bot = bot
        self.author = author

    @discord.ui.button(label="Gerenciar Bugigangas", style=discord.ButtonStyle.green)
    async def open_form(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("Você não pode usar esse botão.", ephemeral=True)
            return

        await interaction.response.send_modal(BugigangaForm(self.bot, self.author))

##  PARTE VOLTADA AO CARREGAMENTO DOS COGS

async def setup(bot):
    await bot.add_cog(Help(bot))
    await bot.add_cog(Redes(bot))
    await bot.add_cog(Faces(bot))
    await bot.add_cog(VoiceControl(bot))
    await bot.add_cog(Bugigangas(bot))
    print("✅ Cog de comandos carregado")
    
