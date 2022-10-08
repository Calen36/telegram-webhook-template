import asyncio
from asyncio import sleep

import aiohttp.web_request
from aiohttp import web
import ssl
import json
from main import set_webhook, get_webhook_status, send_message

CNT = 0

async def foo(request):
    global CNT
    r = await request.json()
    print(request)
    CNT += 1
    num = CNT
    print(f"Start {num}")
    print(r)
    # send_message(chat_id, f'Сообщение {CNT}!')
    await sleep(5)
    print(f"Stop {num}")
    # send_message(chat_id, f'Продолжение {CNT}')


async def handle(request: aiohttp.web_request.Request):
    try:
        loop.create_task(foo(request))
        return web.Response(text='ok')
    except Exception as ex:
        return web.Response(text=str(ex))

        return web.HTTPForbidden()

app = web.Application()
app.add_routes([web.post('/', handle)])

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('ssl/public.pem', 'ssl/private.key')


if __name__ == '__main__':
    set_webhook()
    get_webhook_status()
    loop = asyncio.new_event_loop()
    web.run_app(app, ssl_context=ssl_context, loop=loop)
