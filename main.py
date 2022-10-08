from flask import Flask, request
import json

with open('secr.json') as file:
    secret = json.load(file)
TG_TOKEN = secret['TG_TEST_TOKEN']

app = Flask('Webhooks Receiver')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.headers.get('content-type') == 'application/json':
        data = request.stream.read().decode('utf8')
        return data
    return '<h1>ABRA! CADABRA!</h1>'


from email import message
from http.server import HTTPServer, BaseHTTPRequestHandler




APP_HOST = '0.0.0.0'
APP_PORT = 8000

class SimpleGetHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def _html(self, message):
        content = (f"<html><body><h1>{message}</h1></body></html>")
        return content.encode('utf8')

    def do_GET(self):
        self._set_headers()
        message = 'Kurwa!'
        self.wfile.write(self._html(message))


def run_server(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = (APP_HOST, APP_PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()



if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8080)
    run_server(handler_class=SimpleGetHandler)


