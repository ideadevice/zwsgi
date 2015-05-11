# -*- coding: utf-8 -*-


from gevent import Greenlet

import zmq.green as zmq

from zwsgi.servers import ZMQBaseServer as _original_ZMQBaseServer
from zwsgi.servers import ZMQBaseServerChannel as _original_ZMQBaseServerChannel


class ZMQBaseServerChannelGreenlet(_original_ZMQBaseServerChannel, Greenlet):

    def __init__(self, *args):
        Greenlet.__init__(self)
        _original_ZMQBaseServerChannel.__init__(self, *args)


class ZMQBaseServer(_original_ZMQBaseServer):
    Channel = ZMQBaseServerChannelGreenlet
    poller = zmq.Poller()
