import asyncpg

def get_response():
    print ("resposta")

async def register(member):
    db_con = await asyncpg.connect('postgresql://Hunt_owner:npg_tegZoJX59Spl@ep-shiny-sky-acsw0qxp-pooler.sa-east-1.aws.neon.tech/Hunt?sslmode=require&channel_binding=require')
    
    await db_con.execute('''
        INSERT INTO usuario(id, nome)
        VALUES($1, $2)
        ON CONFLICT (id) DO NOTHING
    ''', member.id, member.name)
    #ESSA PORRA CARREGA OS DADOS DE ID E NOME DE ENTRADA
    #(NÃO SE PREOCUPE, OUTROS CAMPOS COMEÇAM EM NULO OU 0)