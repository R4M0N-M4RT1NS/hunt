import asyncpg
import os
from dotenv import load_dotenv
from typing import Final

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

async def register_ban(user_id: int):
    db_con = await asyncpg.connect(DB_URL)
    await db_con.execute('''
        UPDATE usuario
        SET banido = TRUE
        WHERE id = $1
    ''', user_id)
    await db_con.close()
