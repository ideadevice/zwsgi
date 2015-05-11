# -*- coding: utf-8 -*-

import gevent
from gevent import monkey
monkey.patch_all()

import zmq.green as zmq
import zwsgi.green as zwsgi

from zwsgi.servers import ZMQRouterServer


def main():

    context = zmq.Context()
    poller = zmq.Poller()
    address = 'tcp://127.0.0.1:7000'
    server = ZMQRouterServer(address, context=context, poller=poller)
    server.serve_forever()


if __name__ == "__main__":
    main()
