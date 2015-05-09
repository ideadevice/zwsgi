# -*- coding: utf-8 -*-

from zwsgi.servers import ZMQBaseServer


def main():
    server = ZMQBaseServer('tcp://127.0.0.1:7000')
    server.serve_forever()


if __name__ == "__main__":
    main()
