# -*- coding: utf-8 -*-

import zmq


class ZMQBaseRequestHandlerChannel(object):

    pattern = zmq.PUSH

    def __init__(self, request, context, RequestHandlerClass, address):
        self.context = context
        self.request = request
        self.RequestHandlerClass = RequestHandlerClass
        self.address = address

    def connect(self):
        self.sock = self.context.socket(self.pattern)
        self.sock.linger = 1
        self.sock.connect(self.address)

    def handle(self):
        # import time; time.sleep(0.1)
        print "Handle Request", self.request
        return self.RequestHandlerClass(self.request).handle()

    def send(self, response):
        print "Sending response"
        self.sock.send_multipart(response)
        print "Sent response"

    def disconnect(self):
        self.sock.close()

    def run(self):
        self.connect()
        response = self.handle()
        self.send(response)
        self.disconnect()

    _run = run # to make greenlets work


class ZMQBaseRequestHandler(object):

    def __init__(self, request):
        self.request = request

    def handle(self):
        return self.request
