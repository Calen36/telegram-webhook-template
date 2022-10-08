from asyncio import sleep

import aiohttp.web_request
from aiohttp import web
import ssl
import json
from main import set_webhook, get_webhook_status, send_message

CNT = 0


async def handle(request: aiohttp.web_request.Request):
    global CNT
    try:
        r = await request.json()
        # chat_id = r['message']['chat']['id']
        # message_text = r['message']['text']
        CNT += 1
        num = CNT
        print(f"Start {num}")
        print(r)
        # send_message(chat_id, f'Сообщение {CNT}!')
        await sleep(5)
        print(f"Stop {num}")
        # send_message(chat_id, f'Продолжение {CNT}')

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
    web.run_app(app, ssl_context=ssl_context)