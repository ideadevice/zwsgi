# -*- coding: utf-8 -*-

from .base import ZMQBaseServer


class ZMQRouterDealerServer(ZMQBaseServer):
    pattern = ZMQBaseServer.ROUTER


class ZMQRouterReqServer(ZMQBaseServer):
    pattern = ZMQBaseServer.ROUTER
