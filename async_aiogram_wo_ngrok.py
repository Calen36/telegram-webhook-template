"""Aiogram бот на вебхуках. Всем хорош, но не могу заставить http сервер aiogram работать в случае, когда требуется использовать
самоподписанный ssl сертификат. В этом случае используется утилита ngrok, которая создает тоннель от локальной машины к
машине в домене ngrok.io (который уже имеет нормально подписанный сертифиакт). Для регистрации вебхука испльзуется адрес в домене
ngrok.io, запросы с которого пробрасываются на локальную машину.
Для корректной работы требуется:
1) создать и запустить systemd сервис, который запускает команду ngrok http 8443 --log /root/ngrok/log.log
2) запустить данный скрипт, доменное имя будет взято из логов ngrok'а и присвоено переменной WEBHOOK_URL
"""

import asyncio
import ssl
import sys
import json
import os
from pathlib import Path

from aiohttp import web

import aiogram
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import get_new_configured_app, SendMessage
from aiogram.types import ChatType, ParseMode, ContentTypes
from aiogram.utils.markdown import hbold, bold, text, link

#  Не храним ключи в системе контроля версий
with open('secr.json') as file:
    secret = json.load(file)
TOKEN = secret['TG_PROD_TOKEN']

WEBHOOK_HOST = 'https://999109-cm78017.tmweb.ru:8443'  # Domain name or IP addres which your bot is located.
WEBHOOK_PORT = 8443  # Telegram Bot API allows only for usage next ports: 443, 80, 88 or 8443
WEBHOOK_URL_PATH = ''  # Part of URL


# This options needed if you use self-signed SSL certificate
# Instructions: https://core.telegram.org/bots/self-signed
proj_dir = Path(__file__).resolve().parent
ssl_dir = os.path.join(proj_dir, 'ssl')
WEBHOOK_SSL_CERT = os.path.join(ssl_dir, 'public.pem')
WEBHOOK_SSL_PRIV = os.path.join(ssl_dir, 'private.key')

WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_URL_PATH}"


#   User any available port in range from 1024 to 49151 if you're using proxy, or WEBHOOK_PORT if you're using direct webhook handling
# Характеристики веб-сервера, который поднимает aiogram в режиме работы с вебхуками
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 8443


BAD_CONTENT = ContentTypes.PHOTO & ContentTypes.DOCUMENT & ContentTypes.STICKER & ContentTypes.AUDIO

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def cmd_start(message: types.Message):
    # Yep. aiogram allows to respond into webhook.
    # https://core.telegram.org/bots/api#making-requests-when-getting-updates
    return SendMessage(chat_id=message.chat.id, text='Hi from webhook!',
                       reply_to_message_id=message.message_id)


async def cmd_about(message: types.Message):
    # In this function markdown utils are userd for formatting message text
    return SendMessage(message.chat.id, 'some pesumably fancy text', parse_mode=ParseMode.MARKDOWN)


async def cancel(message: types.Message):
    # Get current state context
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    # If current user in any state - cancel it.
    if await state.get_state() is not None:
        await state.set_state(state=None)
        return SendMessage(message.chat.id, 'Current action is canceled.')
        # Otherwise do nothing


async def unknown(message: types.Message):
    """
    Handler for unknown messages.
    """
    return SendMessage(message.chat.id,
                       f"I don\'t know what to do with content type `{message.content_type()}`. Sorry :c")


async def cmd_id(message: types.Message):
    """
    Return info about user.
    """
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        chat = message.chat
    elif message.forward_from and message.chat.type == ChatType.PRIVATE:
        target = message.forward_from
        chat = message.forward_from or message.chat
    else:
        target = message.from_user
        chat = message.chat

    result_msg = [hbold('Info about user:'),
                  f"First name: {target.first_name}"]
    if target.last_name:
        result_msg.append(f"Last name: {target.last_name}")
    if target.username:
        result_msg.append(f"Username: {target.mention}")
    result_msg.append(f"User ID: {target.id}")

    result_msg.extend([hbold('Chat:'),
                       f"Type: {chat.type}",
                       f"Chat ID: {chat.id}"])
    if chat.type != ChatType.PRIVATE:
        result_msg.append(f"Title: {chat.title}")
    else:
        result_msg.append(f"Title: {chat.full_name}")
    return SendMessage(message.chat.id, '\n'.join(result_msg), reply_to_message_id=message.message_id,
                       parse_mode=ParseMode.HTML)


async def on_startup(app):
    # Demonstrate one of the available methods for registering handlers
    # This command available only in main state (state=None)
    dp.register_message_handler(cmd_start, commands=['start'])

    # This handler is available in all states at any time.
    dp.register_message_handler(cmd_about, commands=['help', 'about'], state='*')
    dp.register_message_handler(unknown, content_types=BAD_CONTENT,
                                func=lambda message: message.chat.type == ChatType.PRIVATE)

    # You are able to register one function handler for multiple conditions
    dp.register_message_handler(cancel, commands=['cancel'], state='*')
    dp.register_message_handler(cancel, func=lambda message: message.text.lower().strip() in ['cancel'], state='*')

    dp.register_message_handler(cmd_id, commands=['id'], state='*')
    dp.register_message_handler(cmd_id, func=lambda message: message.forward_from or
                                                             message.reply_to_message and
                                                             message.chat.type == ChatType.PRIVATE, state='*')

    # Get current webhook status
    webhook = await bot.get_webhook_info()

    # If URL is bad
    if webhook.url != WEBHOOK_URL:
        # If URL doesnt match current - remove webhook
        if not webhook.url:
            await bot.delete_webhook()

        # Set new URL for webhook
        await bot.set_webhook(WEBHOOK_URL, certificate=open(WEBHOOK_SSL_CERT, 'rb'))
        # If you want to use free certificate signed by LetsEncrypt you need to set only URL without sending certificate.


async def on_shutdown(app):
    """
    Graceful shutdown. This method is recommended by aiohttp docs.
    """
    # Remove webhook.
    await bot.delete_webhook()

    # Close Redis connection.
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    # Get instance of :class:`aiohttp.web.Application` with configured router.
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)

    # Setup event handlers.
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Generate SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

    # Start web-application.
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=context)
    # Note:
    #   If you start your bot using nginx or Apache web server, SSL context is not required.
    #   Otherwise you need to set `ssl_context` parameter.