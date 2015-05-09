# -*- coding: utf-8 -*-

import zmq

c = zmq.Context()
sock = c.socket(zmq.DEALER)
sock.connect('tcp://localhost:7000')
request = 'hello world'
sock.send(request)
response = sock.recv()
