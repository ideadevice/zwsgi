# -*- coding: utf-8 -*-

import zmq.green as zmq

from .base import ZMQBaseServer


class ZMQRouterDealerServer(ZMQBaseServer):
    pattern = zmq.ROUTER
    poller = zmq.Poller()


class ZMQRouterReqServer(ZMQBaseServer):
    pattern = zmq.ROUTER
    poller = zmq.Poller()
