# import discord
# from discord.ext import commands, tasks
# import random
# import asyncpg
# import os
# from dotenv import load_dotenv
# from typing import Final

# load_dotenv()
# DB_URL: Final[str] = os.getenv("DB_URL")

# class Encontros(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.dialogos = [
#             {
#                 "texto": "\"Eae, eu to pensando em ir começar a caçar tambem. Mas tipo, meu amigo me disse pra levar uma pedra no dia, tão me zuando ou é verdade isso ai?\"",
#                 "resposta": "sim",
#                 "extra": ["espera", "som"]
#             },
#             # Adicione mais diálogos aqui
#         ]
#         self.ja_responderam = set()
#         self.canal_destino = "teste"  # Nome do canal onde será enviado o encontro
#         self.evento_ativo = None  # Índice do diálogo ativo
#         self.encontro_loop.start()

#     @tasks.loop(count=1)
#     async def encontro_loop(self):
#         await self.bot.wait_until_ready()
#         await self.novo_encontro()

#     async def novo_encontro(self):
#         self.ja_responderam.clear()
#         self.evento_ativo = random.randint(0, len(self.dialogos) - 1)
#         canal = discord.utils.get(self.bot.get_all_channels(), name=self.canal_destino)
#         if canal:
#             await canal.send(f"📢 Evento: {self.dialogos[self.evento_ativo]['texto']}")
#         else:
#             print(f"Canal '{self.canal_destino}' não encontrado.")

#         delay = random.randint(30, 120) * 60  # minutos -> segundos
#         self.encontro_loop.change_interval(seconds=delay)
#         self.encontro_loop.start()

#     @commands.Cog.listener()
#     async def on_message(self, message):
#         if message.author.bot or self.evento_ativo is None:
#             return

#         if message.channel.name != self.canal_destino:
#             return

#         if message.author.id in self.ja_responderam:
#             try:
#                 await message.author.send("Você já respondeu esse encontro.")
#             except discord.Forbidden:
#                 await message.channel.send(f"{message.author.mention}, não consegui enviar uma mensagem privada para você.")
#             return

#         texto = message.content.lower()
#         evento = self.dialogos[self.evento_ativo]

#         if evento['resposta'] in texto:
#             bonus = all(p in texto for p in evento.get("extra", []))
#             ganho = 2 if bonus else 1
#             await self.adicionar_bugigangas(message.author.id, ganho)
#             self.ja_responderam.add(message.author.id)
#             try:
#                 await message.author.send(f"Parabéns. Você ganhou {ganho} bugiganga(s)!")
#             except discord.Forbidden:
#                 await message.channel.send(f"{message.author.mention}, não consegui enviar uma mensagem privada para você.")
#         else:
#             self.ja_responderam.add(message.author.id)
#             try:
#                 await message.author.send("Resposta incorreta. Tente novamente no próximo encontro.")
#             except discord.Forbidden:
#                 await message.channel.send(f"{message.author.mention}, não consegui enviar uma mensagem privada para você.")

#     async def adicionar_bugigangas(self, user_id: int, quantidade: int):
#         db_con = await asyncpg.connect(DB_URL)
#         await db_con.execute('''
#             UPDATE usuario SET bugigangas = bugigangas + $1 WHERE id = $2
#         ''', quantidade, user_id)
#         await db_con.close()

# async def setup(bot):
#     await bot.add_cog(Encontros(bot))
