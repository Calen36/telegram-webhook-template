import json
from pathlib import Path
import os

import requests
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook


proj_dir = Path(__file__).resolve().parent
ssl_dir = os.path.join(proj_dir, 'ssl')
ssl_certificate = os.path.join(ssl_dir, 'public.pem')
ssl_private_key = os.path.join(ssl_dir, 'private.key')
ssl_context = (ssl_certificate, ssl_private_key)

WEBHOOK_HOST = 'https://999109-cm78017.tmweb.ru'
WEBHOOK_PORT = '8443'
WEBHOOK_PATH = '/webhook/astro/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings

WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 8443



with open('secr.json') as file:
    secret = json.load(file)
TG_TOKEN = secret['TG_PROD_TOKEN']

TG_API_URL = f'https://api.telegram.org/bot{TG_TOKEN}/'


def print_dict(d: dict, level=0):
    indent = '\t' * level
    for k, v in d.items():
        if isinstance(v, dict):
            print(f"{indent}{k}:")
            print_dict(v, level=level+1)
        elif isinstance(v, list):
            for entry in v:
                if isinstance(entry, dict):
                    print(f"{indent}{k}:")
                    print_dict(entry, level=level+1)
                else:
                    print(f"{indent}{v}")
        else:
            print(f"{indent}{k}: {v}")


def send_message(chat_id: int, text: str):
    url = TG_API_URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


def get_updates():
    url = TG_API_URL + 'getupdates'
    r = requests.get(url)
    return r.json()


app = Flask('Webhooks Receiver')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST' and request.headers.get('content-type') == 'application/json':
        r = request.get_json()
        print_dict(r)
        try:
            chat_id = r['message']['chat']['id']
            send_message(chat_id, 'тратата!')
        except:
            print('Oй!')
        return jsonify(r)
    return "<h1>Errrr! Let's drink a flask of whiskey!</h1>"





bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    await bot.send_message(message.chat.id, message.text)
    # or reply INTO webhook
    return SendMessage(message.chat.id, message.text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start
    pass


async def on_shutdown(dp):
    # logging.warning('Shutting down..')
    # insert code here to run it before shutdown
    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()
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
        port=WEBHOOK_PORT,
    )




# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8443, ssl_context=ssl_context)
