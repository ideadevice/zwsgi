# -*- coding: utf-8 -*-

from .base import ZMQBaseServer, ZMQBaseServerChannel


class ZMQRepReqServerChannel(ZMQBaseServerChannel):

    def unpack(self):
        self.request = self.ingress[0]

    def pack(self):
        self.egress = [self.response,]


class ZMQRepReqServer(ZMQBaseServer):
    pattern = ZMQBaseServer.REP
    Channel = ZMQRepReqServerChannel


class ZMQRepDealerServer(ZMQRepReqServer):
    """Note: REP assumes a null frame sent by DEALER (client)"""
    pass
