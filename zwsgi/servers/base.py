# -*- coding: utf-8 -*-

"""Base ZMQ server classes.
"""

from threading import Thread

import zmq
from zmq.error import ZMQError

from zwsgi.handlers import ZMQBaseRequestHandler


class ZMQBaseServerChannel(object):

    pattern = zmq.PUSH

    def __init__(self, ingress, context, RequestHandlerClass, address):
        self.context = context
        self.ingress = ingress
        self.RequestHandlerClass = RequestHandlerClass
        self.address = address

    def connect(self):
        self.sock = self.context.socket(self.pattern)
        self.sock.linger = 1
        self.sock.connect(self.address)

    def unpack(self):
        print "Ingress:", self.ingress
        self.request = self.ingress
        print "Request:", self.request

    def handle(self):
        # import time; time.sleep(0.1)
        self.response = self.RequestHandlerClass(self.request).handle()

    def pack(self):
        print "Response:", self.response
        self.egress = self.response
        print "Egress:", self.egress

    def send(self):
        self.sock.send_multipart(self.egress)

    def disconnect(self):
        self.sock.close()

    def run(self):
        self.connect()
        self.unpack()
        self.handle()
        self.pack()
        self.send()
        self.disconnect()

    _run = run # to make greenlets work


class ZMQBaseServerChannelThread(ZMQBaseServerChannel, Thread):

    def __init__(self, *args):
        Thread.__init__(self)
        ZMQBaseServerChannel.__init__(self, *args)


class ZMQBaseServer(object):
    REP = zmq.REP
    REQ = zmq.REQ
    ROUTER = zmq.ROUTER
    DEALER = zmq.DEALER
    PUB = zmq.PUB
    SUB = zmq.SUB
    XPUB = zmq.XPUB
    XSUB = zmq.XSUB
    PULL = zmq.PULL
    PUSH = zmq.PUSH
    PAIR = zmq.PAIR

    protocol = "tcp"
    Channel = ZMQBaseServerChannelThread
    RequestHandlerClass = ZMQBaseRequestHandler
    pattern = None
    poller = zmq.Poller()

    def __init__(self, listener,
                 context=None,
                 handler_class=None):
        self.listener = listener
        self.context = context or zmq.Context.instance()
        self.sock = self.context.socket(self.pattern)
        self.pipe = self.context.socket(zmq.PULL)
        if handler_class is not None:
            self.RequestHandlerClass = handler_class
        self._shutdown_request = False

    @property
    def address(self):
        return "{}://{}:{}".format(self.protocol, self.listener[0], self.listener[1])

    @property
    def sock_closed(self):
        return self.sock.closed if hasattr(self, 'sock') else True

    @property
    def pipe_closed(self):
        return self.pipe.closed if hasattr(self, 'pipe') else True

    def do_close(self):
        pass

    def _handle(self, ingress):
        self.Channel(ingress, self.context, self.RequestHandlerClass, self.pipe_address).start()

    def _accept_pipe(self):
        self.pipe.bind(self.pipe_address)
        self.poller.register(self.pipe, zmq.POLLIN)

    def _accept_sock(self):
        self.sock.bind(self.address)
        self.poller.register(self.sock, zmq.POLLIN)

    def _accept(self):
        self._accept_sock()
        self._accept_pipe()

    def _pre_accept(self):
        self.pipe_address = "inproc://inproc".format(id(self))
        # print "pipe_address {}".format(self.pipe_address)

    def _start_accept(self):
        self._pre_accept()
        self._accept()
        self._post_accept()

    def _post_accept(self):
        pass

    def _eventloop(self):
        # TODO: remove timeout
        # t_ms = 5000
        while not self._shutdown_request:
            try:
                socks = dict(self.poller.poll())
                # print "Got event on socks: {}".format(socks)
                if socks.get(self.sock) == zmq.POLLIN:
                    ingress = self.sock.recv_multipart(zmq.DONTWAIT)
                    # print "ingress", ingress
                    self._handle(ingress)
                if socks.get(self.pipe) == zmq.POLLIN:
                    egress = self.pipe.recv_multipart(zmq.DONTWAIT)
                    # print "egress", egress
                    self.sock.send_multipart(egress)
            except:
                self.do_close()
                raise

    def _serve(self):
        try:
            self._start_accept()
            # print "Starting event loop"
            self._eventloop()
        except:
            self._stop()
            raise

    def _close_sock(self):
        if not self.sock_closed:
            self.sock.close()
            self.poller.unregister(self.sock)

    def _close_pipe(self):
        if not self.pipe_closed:
            self.pipe.close()
            self.poller.unregister(self.pipe)

    def _close(self):
        self._close_sock()
        self._close_pipe()

    def _stop(self):
        self._shutdown_request = True
        self._close()

    def serve_forever(self):
        try:
            self._serve()
        finally:
            self._stop()

    def _formatinfo(self):
        result = ''
        return result

    def __repr__(self):
        return '<%s at %s %s>' % (type(self).__name__, hex(id(self)), self._formatinfo())

    def __str__(self):
        return '<%s at %s %s>' % (type(self).__name__, hex(id(self)), self._formatinfo())
