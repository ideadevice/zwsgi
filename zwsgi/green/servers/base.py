# -*- coding: utf-8 -*-

import zmq.green as zmq

from zwsgi.servers import ZMQBaseServer as _original_ZMQBaseServer


class ZMQBaseServer(_original_ZMQBaseServer):
    poller = zmq.Poller()
