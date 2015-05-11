# -*- coding: utf-8 -*-


from gevent import Greenlet

from zwsgi.servers import ZMQBaseServer as _original_ZMQBaseServer
from zwsgi.channels import ZMQBaseChannel


class ZMQBaseChannelGreenlet(ZMQBaseChannel, Greenlet):

    def __init__(self, *args):
        Greenlet.__init__(self)
        ZMQBaseChannel.__init__(self, *args)


class ZMQBaseServer(_original_ZMQBaseServer):
    Channel = ZMQBaseChannelGreenlet
