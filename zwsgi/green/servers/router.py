# -*- coding: utf-8 -*-

import zmq.green as zmq

from .base import ZMQBaseServer


class ZMQRouterServer(ZMQBaseServer):
    pattern = zmq.ROUTER
    poller = zmq.Poller()
