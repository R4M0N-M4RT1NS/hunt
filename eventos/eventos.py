import asyncpg
import asyncio
import discord
from discord.ext import tasks

# Função chamada quando um novo membro entra
async def register(member):
    db_con = await asyncpg.connect(
        'postgresql://Hunt_owner:npg_tegZoJX59Spl@ep-shiny-sky-acsw0qxp-pooler.sa-east-1.aws.neon.tech/Hunt?sslmode=require&channel_binding=require'
    )

    await db_con.execute('''
        INSERT INTO usuario(id, nome)
        VALUES($1, $2)
        ON CONFLICT (id) DO NOTHING
    ''', member.id, member.name)

    await db_con.close()

# Armazena canais temporários
temp_vc = {}

# Modal para criar o canal temporário
class Temp_vc_Channel(discord.ui.Modal, title="Criar Canal de Voz Temporário"):

    name_vc = discord.ui.TextInput(
        label="Nome do canal de voz",
        placeholder="Ex: Time C",
        max_length=50
    )

    limit_vc = discord.ui.TextInput(
        label="Limite de pessoas",
        placeholder="Ex: 10",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        name_submit = str(self.name_vc)
        try:
            limit_submit = int(str(self.limit_vc))
        except ValueError:
            await interaction.response.send_message("Limite deve ser um número.", ephemeral=True)
            return

        guild = interaction.guild

        chanel = await guild.create_voice_channel(
            name=name_submit,
            user_limit=limit_submit
        )

        temp_vc[chanel.id] = {"canal": chanel}
        await interaction.response.send_message(f"Canal `{name_submit}` pronto para ser usado", ephemeral=True)

# Tarefa de monitoramento dos canais de voz
@tasks.loop(seconds=10)
async def check_vc():
    for id_channel in list(temp_vc.keys()):
        channel = temp_vc[id_channel]["canal"]
        if len(channel.members) == 0:
            await asyncio.sleep(10)
            if len(channel.members) == 0:
                await channel.delete()
                del temp_vc[id_channel]

# Setup de eventos e comandos
async def setup(bot):
    # Slash command: /vc
    @bot.tree.command(name="vc", description="Cria um canal de voz temporário com formulário")
    async def vc(interaction: discord.Interaction):
        await interaction.response.send_modal(Temp_vc_Channel())

    # Evento de novo membro
    @bot.event
    async def on_member_join(member):
        await register(member)

    check_vc.start()