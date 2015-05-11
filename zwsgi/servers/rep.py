# -*- coding: utf-8 -*-

from .base import ZMQBaseServer, ZMQBaseServerChannelThread


class ZMQRepReqServerChannelThread(ZMQBaseServerChannelThread):

    def unpack(self):
        self.request = self.ingress[0]

    def pack(self):
        self.egress = [self.response,]


class ZMQRepReqServer(ZMQBaseServer):
    pattern = ZMQBaseServer.REP
    Channel = ZMQRepReqServerChannelThread


class ZMQRepDealerServer(ZMQRepReqServer):
    pass
