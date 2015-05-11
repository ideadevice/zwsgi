# -*- coding: utf-8 -*-

from .base import ZMQBaseServer, ZMQBaseServerChannel


class ZMQRouterDealerServerChannel(ZMQBaseServerChannel):

    def unpack(self):
        self.identity = self.ingress[0]
        self.request = "".join(self.ingress[1:])

    def pack(self):
        self.egress = [self.identity, self.response]


class ZMQRouterReqServerChannel(ZMQBaseServerChannel):

    def unpack(self):
        self.identity = self.ingress[0]
        self.delimiter = self.ingress[1]
        self.request = "".join(self.ingress[2:])

    def pack(self):
        self.egress = [self.identity, self.delimiter, self.response]


class ZMQRouterDealerServer(ZMQBaseServer):
    pattern = ZMQBaseServer.ROUTER
    Channel = ZMQRouterDealerServerChannel


class ZMQRouterReqServer(ZMQBaseServer):
    pattern = ZMQBaseServer.ROUTER
    Channel = ZMQRouterReqServerChannel
