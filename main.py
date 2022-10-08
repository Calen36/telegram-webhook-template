from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.headers.get('content-type') == 'application/json':
        data = request.stream.read().decode('utf8')
        return data
    return '<h1>ABRA! CADABRA!</h1>'


if __name__ == '__main__':
    app.run(port=8080)