# -*- coding: utf-8 -*-

import zmq

from .base import ZMQBaseServer


class ZMQRouterDealerServer(ZMQBaseServer):
    pattern = zmq.ROUTER


class ZMQRouterReqServer(ZMQBaseServer):
    pattern = zmq.ROUTER
