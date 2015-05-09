# -*- coding: utf-8 -*-

"""Base ZMQ server classes.
"""

import zmq
from zmq.error import ZMQError


class ZMQBaseRequestHandler(object):

    def __init__(self, request, address):
        self.request = request
        context = zmq.Context.instance()
        self.sock = context.socket(zmq.PUSH)
        self.sock.connect(address)

    def send(self, response):
        self.sock.send_multipart(response)

    def _handle(self):
        # import time; time.sleep(0.1)
        # print "Request", self.request
        return self.request

    def handle(self):
        response = self._handle()
        self.send(response)


class ZMQBaseServer(object):

    def __init__(self, address,
                 context=None, poller=None,
                 RequestHandlerClass=ZMQBaseRequestHandler):
        self._shutdown_request = False
        self.address = address
        self.context = context
        self.poller = poller
        self.sock = self.context.socket(self.pattern)
        self.pipe = self.context.socket(zmq.PULL)
        self.RequestHandlerClass = RequestHandlerClass

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        if not hasattr(self, 'context'):
            self._context = context or zmq.Context.instance()

    @property
    def poller(self):
        return self._poller

    @poller.setter
    def poller(self, poller):
        if not hasattr(self, 'poller'):
            self._poller = poller or zmq.Poller()

    @property
    def pattern(self):
        return zmq.ROUTER

    @property
    def protocol(self):
        return self.address.split(':')[0]

    @property
    def interface(self):
        return self.address.split(':')[1].lstrip('//')

    @property
    def port(self):
        return self.address.split(':')[2]

    @property
    def sock_closed(self):
        return self.sock.closed if hasattr(self, 'sock') else True

    @property
    def pipe_closed(self):
        return self.pipe.closed if hasattr(self, 'pipe') else True

    def do_close(self):
        pass

    def _handle(self, request):
        handler = self.RequestHandlerClass(request,
                                           self.pipe_address)
        handler.handle()

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
        self.pipe_address = "inproc://{0}.inproc".format(id(self))

    def _start_accept(self):
        self._pre_accept()
        self._accept()
        self._post_accept()

    def _post_accept(self):
        pass

    def _eventloop(self):
        try:
            socks = dict(self.poller.poll())
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
            while not self._shutdown_request:
                self._eventloop()
        except:
            self._stop()
            raise

    def _close_sock(self):
        if not self.sock_closed:
            self.sock.close()
            self.poller.unregister(self.sock)
        if not self.pipe_closed:
            self.pipe.close()
            self.poller.unregister(self.pipe)

    def _stop(self):
        self._shutdown_request = True
        self._close_sock()

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
