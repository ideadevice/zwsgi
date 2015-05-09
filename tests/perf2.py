# -*- coding: utf-8 -*-

import time
import zmq

from threading import Thread

c = zmq.Context()
sock = c.socket(zmq.DEALER)
sock.connect('tcp://localhost:7000')


n = 0
def monitor():
    global n
    while True:
        time.sleep(1)
        print n, 'reqs/s'
        n = 0

Thread(target=monitor).start()

while True:
    request = 'hi'
    sock.send(request)
    response = sock.recv()
    n += 1
