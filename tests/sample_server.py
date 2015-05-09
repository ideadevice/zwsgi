# -*- coding: utf-8 -*-

import zmq
from zwsgi.servers import ZMQBaseServer


def main():
    server = ZMQBaseServer('tcp://127.0.0.1:7000', zmq.ROUTER)
    server.serve_forever()


if __name__ == "__main__":
    main()
