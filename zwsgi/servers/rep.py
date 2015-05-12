# -*- coding: utf-8 -*-

from .base import ZMQBaseServer, ZMQBaseServerChannel


class ZMQRepReqServerChannel(ZMQBaseServerChannel):

    def unpack(self):
        return self.ingress[0]

    def pack(self, response):
        self.egress = [response,]


class ZMQRepReqServer(ZMQBaseServer):
    pattern = ZMQBaseServer.REP
    Channel = ZMQRepReqServerChannel


class ZMQRepDealerServer(ZMQRepReqServer):
    """Note: REP assumes a null frame sent by DEALER (client)"""
    pass
