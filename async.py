"""З"""

import asyncio
from asyncio import sleep

from aiogram import Bot, Dispatcher

import aiohttp.web_request
from aiohttp import web
import aiohttp
import ssl
from main import set_webhook, get_webhook_status, send_message, TG_TOKEN


bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)



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
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.app = aiohttp.web.Application()
        self.app.add_routes([aiohttp.web.post('/', self.create_request_handler)])
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain('ssl/public.pem', 'ssl/private.key')

    def run(self):
        aiohttp.web.run_app(self.app, ssl_context=self.ssl_context, loop=self.loop)

    def create_request_handler(self, request: aiohttp.web_request.Request):
        self.loop.create_task(handle(request))
        return aiohttp.web.Response(text='ok')



async def create_request_handler(request: aiohttp.web_request.Request):
    loop.create_task(handle(request))
    return web.Response(text='ok')

app = web.Application()
app.add_routes([web.post('/', create_request_handler)])

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('ssl/public.pem', 'ssl/private.key')


if __name__ == '__main__':
    # set_webhook()
    # get_webhook_status()
    # loop = asyncio.new_event_loop()
    # web.run_app(app, ssl_context=ssl_context, loop=loop)

    server = WebhookServer()
    loop = server.loop
    server.run()