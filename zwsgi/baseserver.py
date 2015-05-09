# -*- coding: utf-8 -*-

"""Base ZMQ server classes.
"""

from threading import Thread
from Queue import Queue

import zmq
from zmq.error import ZMQError


class ZMQBaseRequestHandler(object):

    def __init__(self, request, queue):
        self.request = request
        self.queue = queue

    def send(self, response):
        self.queue.put(response)

    def _handle(self):
        return self.request

    def handle(self):
        response = self._handle()
        self.send(response)


class ZMQBaseServerDispatcherThread(Thread):

    def __init__(self, context, poller, pipe_endpoint, out_queue):
        super(ZMQBaseServerDispatcherThread, self).__init__()
        self.out_queue = out_queue
        self.pipe = context.socket(zmq.PAIR)
        self.pipe.connect(pipe_endpoint)
        self.poller = poller
        self.poller.register(self.pipe, zmq.POLLIN)

    def run(self):
        while True:
            self.pipe.send_multipart(self.out_queue.get())


class ZMQBaseServer(object):

    ServerDispatcherThread = ZMQBaseServerDispatcherThread

    def __init__(self, address,
                 context=None, poller=None, ppoller=None,
                 RequestHandlerClass=ZMQBaseRequestHandler):
        self._shutdown_request = False
        self.out_queue = Queue()
        self.address = address
        self.context = context
        self.poller = poller
        self.ppoller = ppoller
        self.socket = self.context.socket(self.pattern)
        self.pipe = self.context.socket(zmq.PAIR)
        self.pipe_endpoint = "inproc://{0}.inproc".format(id(self))
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
    def ppoller(self):
        return self._ppoller

    @ppoller.setter
    def ppoller(self, ppoller):
        if not hasattr(self, 'ppoller'):
            self._ppoller = ppoller or zmq.Poller()

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

    @property
    def pipe_closed(self):
        return self.pipe.closed if hasattr(self, 'pipe') else True

    def do_close(self):
        pass

    def _handle(self, request):
        handler = self.RequestHandlerClass(request, self.out_queue)
        #TODO: Use pool
        Thread(target=handler.handle).start()

    def _start_accepting(self):
        self.socket.bind(self.address)
        self.pipe.bind(self.pipe_endpoint)
        self.poller.register(self.socket, zmq.POLLIN)
        self.poller.register(self.pipe, zmq.POLLIN)
        self._init_handler_thread()

    def _init_handler_thread(self):
        ht = self.ServerDispatcherThread(self.context,
                                         self.ppoller,
                                         self.pipe_endpoint,
                                         self.out_queue,
        )
        ht.start()

    def _eventloop(self):
        try:
            socks = dict(self.poller.poll())
            if socks.get(self.socket) == zmq.POLLIN:
                request = self.socket.recv_multipart(zmq.DONTWAIT)
                self._handle(request)
            if socks.get(self.pipe) == zmq.POLLIN:
                response = self.pipe.recv_multipart(zmq.DONTWAIT)
                self.socket.send_multipart(response)
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
        if not self.pipe_closed:
            self.pipe.close()
            self.poller.unregister(self.pipe)

    def _stop(self):
        self._shutdown_request = True
        self._close_socket()

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
        return '<%s %s>' % (type(self).__name__, self._formatinfo())
