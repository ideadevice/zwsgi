# -*- coding: utf-8 -*-

import zmq.green as zmq

from .base import ZMQBaseServer


class ZMQRepReqServer(ZMQBaseServer):
    pattern = zmq.REP
    poller = zmq.Poller()
