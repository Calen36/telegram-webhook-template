import json
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
from flask import Flask, request, jsonify

DEBUG = False

with open('secr.json') as file:
    secret = json.load(file)
if DEBUG:
    TG_TOKEN = secret['TG_TEST_TOKEN']
else:
    TG_TOKEN = secret['TG_PROD_TOKEN']


URL = f'https://api.telegram.org/bot{TG_TOKEN}/'


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
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


def get_updates():
    url = URL + 'getupdates'
    r = requests.get(url)
    return r.json()


def main():
    # r = requests.get(URL + 'getMe')
    # print_dict(r.json())
    r = get_updates()
    try:
        chat_id = r['result'][-1]['message']['chat']['id']
        send_message(chat_id, 'тратата!')
    except:
        print('cant get chat id')


# РЕАЛИЗАЦИЯ ЧЕРЕЗ FLASK
app = Flask('Webhooks Receiver')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST' and request.headers.get('content-type') == 'application/json':
        # data = request.stream.read().decode('utf8')
        # return data
        r = request.get_json()
        print_dict(r)
        return jsonify(r)
    return "<h1>Errrr! Let's drink a flask of whiskey!</h1>"

# РЕАЛИЗАЦИЯ ЧЕРЕЗ СТАНДАРТНУЮ БИБЛИОТЕКУ


APP_HOST = '0.0.0.0'
APP_PORT = 8000


class SimpleGetHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def _html(self, message):
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode('utf8')

    def do_GET(self):
        self._set_headers()
        message = 'Kurwa!'
        self.wfile.write(self._html(message))

    def do_POST(self):
        self._set_headers()
        message = 'Kurwa!'
        self.wfile.write(self._html(message))


def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = (APP_HOST, APP_PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

webhook_url = URL + 'setWebhook?url=https://999109-cm78017.tmweb.ru:8443/'
getMe_url = URL+'getMe'

if __name__ == '__main__':
    print(webhook_url)
    print(getMe_url)
    # app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')
    # run_server(handler_class=SimpleGetHandler)
    # main()