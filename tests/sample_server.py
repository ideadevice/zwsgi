# -*- coding: utf-8 -*-

import zmq
from zwsgi.servers import ZMQRouterServer


def main():
    server = ZMQRouterServer('tcp://127.0.0.1:7000')
    server.serve_forever()


if __name__ == "__main__":
    main()
