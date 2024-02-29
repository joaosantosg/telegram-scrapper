from telethon import TelegramClient, events
from datetime import timedelta
from models.CanalModel import CanalModel
import asyncio
import logging
from aiosqlite import connect
from config import Telegram
import re

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram-scrapper")

CANAIS_FILTRADOS =  Telegram.CANAIS_FILTRADOS

def converter_data(data):
    data_utc = data - timedelta(hours=3)
    return data_utc.strftime("%d/%m/%Y %H:%M")


def remover_acentos(texto):
    # Dicionário de mapeamento de caracteres acentuados para não acentuados
    mapa_acentos = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C'
    }
    
    # Utiliza expressão regular para substituir os caracteres acentuados
    texto_sem_acentos = ''.join(mapa_acentos.get(char, char) for char in texto)
    
    return texto_sem_acentos

async def montar_mensagem(evento, palavra_chave, canal):
        data = converter_data(evento.message.date)
        if canal:
            titulo = f"{canal}"
        else:
            titulo = f"Não encontrado"
            
            
        return f"**Nova mensagem do canal:**\n\n" \
            f"**Conteúdo:**\n\n {evento.message.text}\n" \
            f"**Enviado por**: {titulo}\n" \
            f"**Palavra-chave encontrada:** `{palavra_chave}`\n" \
            f"**Data e hora:** {data}\n"

async def busca_nome_canal(evento):
    async with connect("mydatabase.db") as conexao:
        canal = await buscar_canal_por_numero(numero=evento.message.chat_id, conexao=conexao)
        if canal:
            return canal[1]
        else:
            await atualizar_canais()
            canal = await buscar_canal_por_numero(numero=evento.message.chat_id, conexao=conexao)
            
            if canal:
                return canal[1]
            else:
                return "Canal não encontrado"
                

palavras_chave = [
    "qatar",
    "british",
    "iberia",
    "ibéria",
    "avios",
]


async def tabela_existe(nome_tabela, conexao):
    async with conexao.cursor() as cursor:
        await cursor.execute(
            f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'"
        )
        existe = (await cursor.fetchone())[0] == 1
    return existe


async def criar_tabela(nome_tabela, conexao):
    try:
        async with conexao.cursor() as cursor:
            await cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {nome_tabela} (id INTEGER PRIMARY KEY, nome TEXT, numero INTEGER)"
            )
    except Exception as e:
        log.error(f"Erro ao criar tabela {nome_tabela}: {e}")


async def criar_canal_se_nao_existir(canal: CanalModel, conexao):
    try:
        async with conexao.cursor() as cursor:
            await cursor.execute(
                f"SELECT * FROM canais WHERE numero = ?", (canal.numero,)
            )
            if await cursor.fetchone() is None:
                await cursor.execute(
                    f"INSERT INTO canais (nome, numero) VALUES (?, ?)",
                    (canal.nome, canal.numero),
                )
                await conexao.commit()
                return True
    except Exception as e:
        log.error(f"Erro ao criar canal {canal.nome}: {e}")
    return False


async def buscar_todos_canais(conexao):
    try:
        async with conexao.cursor() as cursor:
            await cursor.execute("SELECT * FROM canais")
            canais = await cursor.fetchall()
            return canais
    except Exception as e:
        log.error(f"Erro ao buscar canais: {e}")
        return []


async def buscar_canal_por_numero(numero, conexao):
    try:
        async with conexao.cursor() as cursor:
            await cursor.execute("SELECT * FROM canais WHERE numero = ?", (numero,))
            canal = await cursor.fetchone()

            return canal
    except Exception as e:
        log.error(f"Erro ao buscar canal: {e}")
        return None


async def atualizar_canais():
    try:
        async with connect("mydatabase.db") as conexao:
            if not await tabela_existe("canais", conexao):
                log.info("Tabela canais não existe, criando...")
                await criar_tabela("canais", conexao)
            canais = await buscar_todos_canais(conexao)
            canais_a_atualizar = []
            async for dialogo in cliente.iter_dialogs():
                if dialogo.id not in [canal[2] for canal in canais]:
                    canais_a_atualizar.append(dialogo)
            for dialogo in canais_a_atualizar:
                await criar_canal_se_nao_existir(CanalModel(nome=dialogo.title, numero=dialogo.id), conexao)

            return True
    except Exception as e:
        log.error(f"Erro ao atualizar canais: {e}")
        return False


async def enviar_mensagem(usuarios, mensagem):
    for usuario in usuarios:
        log.info(f"Enviando mensagem para {usuario}")
        await cliente.send_message(usuario, mensagem)


async def inicializar():
    log.info("ATUALIZANDO CANAIS...")
    await atualizar_canais()
    log.info("CANAIS ATUALIZADOS")
    return True


async def main():
    global cliente 
    log.info("Iniciando telegram scrapper...")
    log.info("Canais a serem filtrados: " + str(CANAIS_FILTRADOS))
    log.info("Pessoas notificadas: " + str(Telegram.LISTENER_CHANNELS))
    cliente = TelegramClient(Telegram.USERNAME, Telegram.API_ID, Telegram.API_HASH)
    await cliente.start()
    await inicializar()
    log.info("Iniciando loop de eventos...")
    
    @cliente.on(events.NewMessage())
    async def ouvinte_nova_mensagem(evento):
        mensagem = remover_acentos(evento.message.text.lower())
        data = converter_data(evento.message.date)
        log.info(f"Nova mensagem recebida: {data}")

        for palavra_chave in palavras_chave:
            if palavra_chave in mensagem:
                canal = await busca_nome_canal(evento)
                log.info("Canal: " + str(canal))
                log.info("Checando se canal está na lista de canais filtrados: " + str(canal) + " " + str(CANAIS_FILTRADOS))
                log.info(canal in CANAIS_FILTRADOS)
                if canal in  CANAIS_FILTRADOS:
                    logging.info(f"Palavra-chave encontrada: {palavra_chave}, através do canal: {canal}, enviando mensagem...")
                    modelo_mensagem = await montar_mensagem(evento, palavra_chave, canal)
                    usuarios = Telegram.LISTENER_CHANNELS
                    await enviar_mensagem(usuarios, modelo_mensagem)
                    break
       
    log.info("Loop de eventos iniciado")
    await cliente.run_until_disconnected()
    log.info("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
