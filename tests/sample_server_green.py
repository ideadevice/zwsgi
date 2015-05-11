# -*- coding: utf-8 -*-

import gevent
from gevent import monkey
monkey.patch_all()

from zwsgi.green.servers import ZMQRouterServer


def main():

    server = ZMQRouterServer(('127.0.0.1', 7000))
    server.serve_forever()


if __name__ == "__main__":
    main()
