# -*- coding: utf-8 -*-

import gevent
from gevent import monkey
monkey.patch_all()

import zmq.green as zmq
from zwsgi.baseserver import ZMQBaseServer


def main():

    context = zmq.Context()
    poller = zmq.Poller()
    ppoller = zmq.Poller()
    address = 'tcp://127.0.0.1:7000'
    server = ZMQBaseServer(address, context=context, poller=poller, ppoller=ppoller)
    server.serve_forever()

if __name__ == "__main__":
    main()