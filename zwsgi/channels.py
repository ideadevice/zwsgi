# -*- coding: utf-8 -*-

import zmq


class ZMQBaseRequestHandlerChannel(object):

    pattern = zmq.PUSH

    def __init__(self, ingress, context, RequestHandlerClass, address):
        self.context = context
        self.ingress = ingress
        self.RequestHandlerClass = RequestHandlerClass
        self.address = address

    def connect(self):
        self.sock = self.context.socket(self.pattern)
        self.sock.linger = 1
        self.sock.connect(self.address)

    def unpack(self):
        print "Ingress:", self.ingress
        self.request = self.ingress
        print "Request:", self.request

    def handle(self):
        # import time; time.sleep(0.1)
        self.response = self.RequestHandlerClass(self.request).handle()

    def pack(self):
        print "Response:", self.response
        self.egress = self.response
        print "Egress:", self.egress

    def send(self):
        self.sock.send_multipart(self.egress)

    def disconnect(self):
        self.sock.close()

    def run(self):
        self.connect()
        self.unpack()
        self.handle()
        self.pack()
        self.send()
        self.disconnect()

    _run = run # to make greenlets work
