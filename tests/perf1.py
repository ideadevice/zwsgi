# -*- coding: utf-8 -*-

import time
from sample_client import client, run


def main():
    sock = client()
    while True:
        start = time.time()
        run(sock)
        end = time.time()
        print end - start


if __name__ == '__main__':
    main()
