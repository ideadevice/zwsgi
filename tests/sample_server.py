# -*- coding: utf-8 -*-

import zmq
from zwsgi.servers import *


def main():
    server = ZMQRouterDealerServer(('127.0.0.1', 7000))
    print server
    server.serve_forever()


if __name__ == "__main__":
    main()
