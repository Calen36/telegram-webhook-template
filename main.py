import json
from pathlib import Path
import os

import requests
from flask import Flask, request, jsonify


proj_dir = Path(__file__).resolve().parent
ssl_dir = os.path.join(proj_dir, 'ssl')
ssl_certificate = os.path.join(ssl_dir, 'public.pem')
ssl_private_key = os.path.join(ssl_dir, 'private.key')
ssl_context = (ssl_certificate, ssl_private_key)

webhook_url = "https://999109-cm78017.tmweb.ru"

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

def set_webhook():
    with open(ssl_certificate) as file:
        certificate = file.read()
    url = TG_API_URL + '/setwebhook'
    headers = {'url': f'{webhook_url}'}
    files = {'certificate': certificate}
    r = requests.post(url=url, headers=headers, files=files)
    print(r.text, r.content)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST' and request.headers.get('content-type') == 'application/json':
        r = request.get_json()
        print_dict(r)
        try:
            chat_id = r['message']['chat']['id']
            send_message(chat_id, 'тратата!')
        except Exception as ex:
            print('Oй!', ex)
        return jsonify(r)
    return "<h1>Errrr! Let's drink a flask of whiskey!</h1>"


if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=8443, ssl_context=ssl_context)
