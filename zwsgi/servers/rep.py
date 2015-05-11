# -*- coding: utf-8 -*-

import zmq

from .base import ZMQBaseServer


class ZMQRepReqServer(ZMQBaseServer):
    pattern = zmq.REP
