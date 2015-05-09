# -*- coding: utf-8 -*-

import time
from threading import Thread

from sample_client import client, run

n = 0

def monitor():
    global n
    while True:
        time.sleep(1)
        print n, 'reqs/s'
        n = 0


def main():
    global n

    Thread(target=monitor).start()
    sock = client()
    while True:
        run(sock)
        n += 1

if __name__ == '__main__':
    main()
