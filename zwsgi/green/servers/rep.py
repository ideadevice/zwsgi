# -*- coding: utf-8 -*-

from .base import ZMQBaseServer


class ZMQRepReqServer(ZMQBaseServer):
    pattern = ZMQBaseServer.REP
