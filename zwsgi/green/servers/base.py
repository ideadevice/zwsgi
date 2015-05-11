# -*- coding: utf-8 -*-


from gevent import Greenlet

from zwsgi.servers import ZMQBaseServer as _original_ZMQBaseServer
from zwsgi.handlers import ZMQBaseRequestHandlerChannel


class ZMQBaseRequestHandlerGreenlet(ZMQBaseRequestHandlerChannel, Greenlet):

    def __init__(self, *args):
        Greenlet.__init__(self)
        ZMQBaseRequestHandlerChannel.__init__(self, *args)


class ZMQBaseServer(_original_ZMQBaseServer):
    RequestHandlerChannel = ZMQBaseRequestHandlerGreenlet
