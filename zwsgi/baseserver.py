# -*- coding: utf-8 -*-

"""Base ZMQ server classes.
"""

import zmq
from zmq.error import ZMQError
import time


class ZMQBaseRequestHandler(object):

    def __init__(self, request):
        self.request = request

    def handle(self):
        response = self.request
        return response


class ZMQBaseServer(object):

    def __init__(self, address,
                 context=None, poller=None,
                 RequestHandlerClass=ZMQBaseRequestHandler):
        self._shutdown_request = False
        self.address = address
        self.context = context
        self.poller = poller
        self.socket = self.context.socket(self.pattern)
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
    def socket_closed(self):
        return self.socket.closed if hasattr(self, 'socket') else True

    def do_close(self):
        pass

    def _recv(self):
        return self.socket.recv_multipart(zmq.DONTWAIT)

    def _handle(self, request):
        return self.RequestHandlerClass(request).handle()

    def _send(self, message):
        return self.socket.send_multipart(message)

    def _start_accepting(self):
        self.socket.bind(self.address)
        self.poller.register(self.socket, zmq.POLLIN)

    def _eventloop(self):
        try:
            socks = dict(self.poller.poll())
            if socks.get(self.socket) == zmq.POLLIN:
                request = self._recv()
                response = self._handle(request)
                self._send(response)
        except:
            self.do_close()
            raise

    def _serve(self):
        try:
            self._start_accepting()
            while not self._shutdown_request:
                self._eventloop()
        except:
            self._stop()
            raise

    def _close_socket(self):
        if not self.socket_closed:
            self.socket.close()
            self.poller.unregister(self.socket)

    def _stop(self):
        self._shutdown_request = True
        self._close_socket()

    def serve(self):
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
        return '<%s %s>' % (type(self).__name__, self._formatinfo())
