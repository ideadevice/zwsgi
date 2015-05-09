# -*- coding: utf-8 -*-


import time
import zmq

c = zmq.Context()
sock = c.socket(zmq.DEALER)
sock.connect('tcp://localhost:7000')

while True:

    start = time.time()
    request = 'hello world'
    sock.send(request)
    response = sock.recv()
    end = time.time()
    print end - start
