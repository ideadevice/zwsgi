# -*- coding: utf-8 -*-


class ZMQBaseRequestHandler(object):

    def __init__(self, request):
        self.request = request

    def handle(self):
        return self.request
