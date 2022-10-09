"""Простой синхронный вебхук-сервер на Фласке. Предполагает использование синхронного телеграм-бота.
"""

import json
from pathlib import Path
import os

import requests
from flask import Flask, request

proj_dir = Path(__file__).resolve().parent
ssl_dir = os.path.join(proj_dir, 'ssl')
ssl_certificate = os.path.join(ssl_dir, 'public.pem')
ssl_private_key = os.path.join(ssl_dir, 'private.key')
ssl_context = (ssl_certificate, ssl_private_key)
webhook_url = "https://999109-cm78017.tmweb.ru:8443"

# не храним ключи в коде
with open('secr.json') as file:
    secret = json.load(file)
TG_TOKEN = secret['TG_PROD_TOKEN']
TG_API_URL = f'https://api.telegram.org/bot{TG_TOKEN}/'


def send_message(chat_id: int, text: str):
    url = TG_API_URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


def set_webhook():
    """Устанавливаем вебхук с самоподписанным ssl сертификатом"""
    with open(ssl_certificate, 'rb') as cert_file:
        certificate = cert_file.read()
    url = TG_API_URL + 'setwebhook'
    data = {'url': f'{webhook_url}'}
    files = {'certificate': certificate}
    requests.post(url=url, data=data, files=files)


def get_webhook_status():
    """Выводим информацию о состоянии вебхука"""
    url = TG_API_URL + 'getWebhookInfo'
    r = requests.get(url)
    verbose_json = json.dumps(r.json(), indent=4)
    print('*' * 100, '\nWEBHOOK STATUS:')
    print(verbose_json)
    print()


app = Flask('Webhooks Receiver')


@app.route('/', methods=['POST'])
def index():
    """Простейший маршрутизатор фласка - если в пришедшем POST запросе есть джейсон - пытается парсить его как
    сообщение телеграма"""
    if request.headers.get('content-type') == 'application/json':
        r = request.get_json()
        try:
            chat_id = r['message']['chat']['id']
            message_text = r['message']['text']
            send_message(chat_id, f'Cам ты {message_text}!')  # простейшая эхо-отвечалка. заменить на что-то вменяемое
        except Exception as ex:
            print('Oй!', ex)
    return "ok"


if __name__ == '__main__':
    set_webhook()
    get_webhook_status()
    app.run(host='0.0.0.0', port=8443, ssl_context=ssl_context)
