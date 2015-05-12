# -*- coding: utf-8 -*-

from flask import Flask, request
app = Flask(__name__)

from zwsgi import monkey
monkey.patch_all()

from zwsgi.servers import ZMQRouterDealerServer as WSGIServer


@app.route('/ping')
def hello_world():
    return 'Hello World!'


def main():
    server = WSGIServer(('127.0.0.1', 7000), app)
    print server
    server.serve_forever()


if __name__ == "__main__":
    main()
