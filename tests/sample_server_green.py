# -*- coding: utf-8 -*-

import gevent
from gevent import monkey
monkey.patch_all()

import zwsgi.green as zwsgi
from zwsgi.servers import ZMQRouterServer


def main():

    address = 'tcp://127.0.0.1:7000'
    server = ZMQRouterServer(address)
    server.serve_forever()


if __name__ == "__main__":
    main()
