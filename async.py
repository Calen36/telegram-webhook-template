import json

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiogram.types.input_file import InputFile

with open('secr.json') as file:
    secret = json.load(file)
API_TOKEN = secret['TG_PROD_TOKEN']
TG_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/'

# webhook settings
WEBHOOK_HOST = 'https://999109-cm78017.tmweb.ru:8443'
WEBHOOK_PATH = ''  # /path/to/api
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 8443

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    # await bot.send_message(message.chat.id, message.text)
    # or reply INTO webhook
    # return SendMessage(message.chat.id, message.text)
    print('!!'*50)
    print(message.text)


async def on_startup(dp):
    certificate = InputFile('ssl/public.pem')
    print('**'*40)
    await bot.set_webhook(WEBHOOK_URL, certificate=certificate)
    x = await bot.get_webhook_info()
    print(x)
    # insert code here to run it after start


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
