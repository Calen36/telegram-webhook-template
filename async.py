""""""
import json
import asyncio
from asyncio import sleep

import requests
from aiogram import Bot, Dispatcher

import aiohttp.web_request
from aiohttp import web
import aiohttp
import ssl

with open('secr.json') as file:
    secret = json.load(file)
TG_TOKEN = secret['TG_PROD_TOKEN']

WEBHOOK_URL = "https://999109-cm78017.tmweb.ru:8443"


bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


CNT = 0
async def handle(request):
    try:
        global CNT
        r = await request.json()
        chat_id = r['message']['chat']['id']
        print(request)
        CNT += 1
        num = CNT
        print(f"Start {num}")
        print(r)
        await bot.send_message(chat_id=chat_id, text='!!!!')
        # send_message(chat_id, f'Сообщение {CNT}!')
        await sleep(5)
        print(f"Stop {num}")
        # send_message(chat_id, f'Продолжение {CNT}')
    except Exception as ex:
        print('oops', ex)


class WebhookServer:
    """Async server for Telegram webhook requests.
    Https server listening on all network interfaces on port 8443 (0.0.0.0:8443) for POST requests.
    After reciving creates handling coroutine in event loop"""
    def __init__(self, tg_api_key: str, webhook_url: str, ssl_public_cert_path: str, ssl_private_key_path: str):
        self.loop = asyncio.new_event_loop()
        self.app = aiohttp.web.Application()
        self.app.add_routes([aiohttp.web.post('/', self.create_request_handler)])
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain(ssl_public_cert_path, ssl_private_key_path)
        self.ssl_public_cert_path = ssl_public_cert_path
        self.tg_api_key = tg_api_key
        self.tg_api_url = f'https://api.telegram.org/bot{tg_api_key}/'
        self.webhook_url = webhook_url

        self.set_webhook()

    def set_webhook(self):
        with open(self.ssl_public_cert_path, 'rb') as file:
            certificate = file.read()
        url = self.tg_api_url + 'setwebhook'
        data = {'url': f'{self.webhook_url}'}
        files = {'certificate': certificate}
        requests.post(url=url, data=data, files=files) # TODO переписать на aiohttp

    def run(self):
        aiohttp.web.run_app(self.app, ssl_context=self.ssl_context, loop=self.loop)

    def create_request_handler(self, request: aiohttp.web_request.Request):
        self.loop.create_task(handle(request))
        return aiohttp.web.Response(text='ok')



if __name__ == '__main__':
    # set_webhook()
    # get_webhook_status()

    server = WebhookServer(tg_api_key=TG_TOKEN,
                           webhook_url=WEBHOOK_URL,
                           ssl_public_cert_path='ssl/public.pem',
                           ssl_private_key_path='ssl/private.key')
    server.run()