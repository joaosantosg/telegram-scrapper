import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from datetime import  timedelta
load_dotenv()

listener_channel = os.getenv("TelegramListenerChannel")

keywords = [
    "qatar", "qatar airways",
    "british", "british airways",
    "iberia", "iberia airlines",
    "avios"
]

username = os.getenv("TelegramUsername")
phone = os.getenv("TelegramPhone")
api_id = os.getenv("TelegramApiId")
api_hash = os.getenv("TelegramApiHash")

client = TelegramClient(username, api_id, api_hash)


def convert_date(date):
    dateUtc = date - timedelta(hours=3)
    return  dateUtc.strftime("%d/%m/%Y %H:%M")

def mount_message(event, keyword, channel):
    date = convert_date(event.message.date)

    return  f"**Nova mensagem do canal:**\n\n" \
            f"**Canal:** [{event.chat.title}]({channel})\n" \
            f"**Usuário:** {event.message.sender.username}\n" \
            f"**Nome:** {event.message.sender.first_name}\n" \
            f"**Conteúdo:** {event.message.message}\n" \
            f"**Palavra-chave encontrada:** `{keyword}`\n" \
            f"**Data e hora:** {date}\n" \
            f"**Link para o canal:** [{channel}]({channel})"

async def send_message(users, message):
    for user in users:
        await client.send_message(user, message)

@client.on(events.NewMessage(chats=listener_channel))
async def newMessageListener(event):
    message = event.message.message.lower()
    date = convert_date(event.message.date)
    print(f"Nova mensagem no canal {event.chat.title}: {date}")
    for keyword in keywords:
        if keyword in message:
            message_template = mount_message(event, keyword, listener_channel)

            users = ['@jaozinj']  # Add usernames here
            
            await send_message(users, message_template)
            break

with client:
    client.run_until_disconnected()
