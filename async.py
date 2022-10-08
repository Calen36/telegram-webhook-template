from aiohttp import web
import ssl
import json
from main import set_webhook, get_webhook_status


async def handle(request):
    text = await request.json()
    print(text)
    return web.Response(text='ok')
    # return web.HTTPForbidden

app = web.Application()
app.add_routes([web.post('/', handle)])

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('ssl/public.pem', 'ssl/private.key')


if __name__ == '__main__':
    set_webhook()
    get_webhook_status()
    web.run_app(app, ssl_context=ssl_context)