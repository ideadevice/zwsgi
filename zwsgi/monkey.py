# -*- coding: utf-8 -*-

import zmq

_Poller = zmq.Poller

def patch_all():
    global _Poller

    from gevent import monkey
    import zmq.green

    monkey.patch_all()
    _Poller = zmq.green.Poller
