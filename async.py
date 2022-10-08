import asyncio
from asyncio import sleep

from aiogram import Bot, Dispatcher

import aiohttp.web_request
from aiohttp import web
import ssl
from main import set_webhook, get_webhook_status, send_message, TG_TOKEN


bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)



CNT = 0

async def foo(request):
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


async def create_request_handler(request: aiohttp.web_request.Request):
    loop.create_task(foo(request))
    return web.Response(text='ok')


app = web.Application()
app.add_routes([web.post('/', create_request_handler)])

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('ssl/public.pem', 'ssl/private.key')


if __name__ == '__main__':
    set_webhook()
    get_webhook_status()
    loop = asyncio.new_event_loop()
    web.run_app(app, ssl_context=ssl_context, loop=loop)
