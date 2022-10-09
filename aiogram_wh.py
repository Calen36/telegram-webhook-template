import json

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiogram.types.input_file import InputFile

USE_NGROK = True

#  Не храним ключи в системе контроля версий
with open('secr.json') as file:
    secret = json.load(file)
API_TOKEN = secret['TG_PROD_TOKEN']

TG_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/'

WEBHOOK_PATH = ''  # /path/to/api

if USE_NGROK:
    """Вариант вебхука через ngrok. Вебхук-запросы приходят на адрес NGROK_URL (ngrok.io имеет подписанный сертификат), и
    оотуда через туннель редиректятся на http-сервер aiogram"""
    WEBHOOK_URL = "https://a652-176-221-149-31.eu.ngrok.io"
else:
    """Вариант вебхуха средствами http-сервера aiogram. Не могу заставить работать в случае, когда требуется использовать
     самоподписанный ssl сертификат."""
    WEBHOOK_HOST = 'https://999109-cm78017.tmweb.ru:8443'
    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


# Характеристики веб-сервера, который поднимает aiogram в режиме работы с вебхуками
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 8443

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(Text(contains='дурак', ignore_case=True))
async def durak(message: types.Message):
    msg = f"Сам {message.text}!"
    return SendMessage(message.chat.id, msg)


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    # await bot.send_message(message.chat.id, message.text)
    # or reply INTO webhook
    msg = f"Все говорят:\n{message.text}\nА ты купи слона!"
    return SendMessage(message.chat.id, msg)


async def on_startup(dp):
    """Регистрируем вебхук при старте приложения.
    Вариант когда не используется ngrok и предоставляется самоподписанный сертификат представлен тут как возможный задел
    на будущее, т.к. пока не могу заставить http сервер aiogram отдавать сертификат."""
    print('**' * 40)
    await bot.set_webhook(WEBHOOK_URL, certificate=None if USE_NGROK else InputFile('ssl/public.pem'))
    info = await bot.get_webhook_info()
    print(info)


async def on_shutdown(dp):
    # insert code here to run it before shutdown
    # Remove webhook (not acceptable in some cases)
    # await bot.delete_webhook()
    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


