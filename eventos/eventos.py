import asyncpg
import asyncio
import discord
from dotenv import load_dotenv
from typing import Final
import os
from discord.ext import tasks

load_dotenv()
DB_URL: Final[str] = os.getenv("DB_URL")

async def register(member):
    db_con = await asyncpg.connect(DB_URL)

    await db_con.execute('''
        INSERT INTO usuario(id, nome)
        VALUES($1, $2)
        ON CONFLICT (id) DO NOTHING
    ''', member.id, member.name)

    await db_con.close()
    #ESSA PORRA CARREGA OS DADOS DE ID E NOME DE ENTRADA
    #(NÃO SE PREOCUPE, OUTROS CAMPOS COMEÇAM EM NULO OU 0)

async def register_ban(user_id: int):
    db_con = await asyncpg.connect(DB_URL)

    await db_con.execute('''
        UPDATE usuario
        SET banido = TRUE
        WHERE id = $1
    ''', user_id)

    await db_con.close()
    # ESSE REGISTRA OS BANS QUE FORAM DADOS, MESMO QUE SEJA DESBANIDO, O USUÁRIO CONTINUA MARCADO