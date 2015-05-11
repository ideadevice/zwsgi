# -*- coding: utf-8 -*-

import zmq

from .base import ZMQBaseServer


class ZMQRouterServer(ZMQBaseServer):
    pattern = zmq.ROUTER
