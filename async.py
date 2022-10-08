import aiohttp.web_request
from aiohttp import web
import ssl
import json
from main import set_webhook, get_webhook_status, send_message


async def handle(request: aiohttp.web_request.Request):
    try:
        r = await request.json()
        chat_id = r['message']['chat']['id']
        message_text = r['message']['text']
        send_message(chat_id, f'Cам ты {message_text}!')

        return web.Response(text='ok')
    except:
        return web.HTTPForbidden()

app = web.Application()
app.add_routes([web.post('/', handle)])

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('ssl/public.pem', 'ssl/private.key')


if __name__ == '__main__':
    set_webhook()
    get_webhook_status()
    web.run_app(app, ssl_context=ssl_context)