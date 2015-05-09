# -*- coding: utf-8 -*-

"""Base ZMQ server classes.
"""

from threading import Thread, Event
import uuid

import zmq
from zmq.error import ZMQError


class ZMQBaseRequestHandler(object):

    def __init__(self, request):
        self.request = request

    def handle(self):
        response = self.request
        return response


class ZMQRequestHandlerThread(Thread):

    def __init__(self, RequestHandlerClass, context, poller, pipe_endpoint):
        super(ZMQRequestHandlerThread, self).__init__()
        self.RequestHandlerClass = RequestHandlerClass
        self.pipe = context.socket(zmq.PAIR)
        self.pipe.linger = 1
        self.pipe.connect(pipe_endpoint)
        self.poller = poller
        self.poller.register(self.pipe, zmq.POLLIN)

    def handler(self, request):
        response = self.RequestHandlerClass(request).handle()
        return response

    def run(self):
        while True:
            socks = dict(self.poller.poll())
            if socks.get(self.pipe) == zmq.POLLIN:
                message = self.pipe.recv_multipart()
                request = message
                # print "request", request
                response = self.handler(request)
                # print "response", response
                self.pipe.send_multipart(response)


class ZMQBaseServer(object):

    def __init__(self, server,
                 context=None, poller=None, ppoller=None,
                 RequestHandlerClass=ZMQBaseRequestHandler):
        self._shutdown_request = False
        self._stop_event = Event()
        self._stop_event.set()
        self.context = context
        self.poller = poller
        self.ppoller = ppoller
        self.server = server
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
    def server(self):
        return self._server

    @server.setter
    def server(self, server):
        self._server = server

    @property
    def RequestHandlerClass(self):
        return self._RequestHandlerClass

    @RequestHandlerClass.setter
    def RequestHandlerClass(self, RequestHandlerClass):
        if not hasattr(self, 'RequestHandlerClass'):
            self._RequestHandlerClass = RequestHandlerClass

    @property
    def pattern(self):
        if isinstance(self.server, tuple):
            return self.server[0]

    @property
    def protocol(self):
        if isinstance(self.server, tuple):
            return self.server[1]

    @property
    def interface(self):
        if isinstance(self.server, tuple):
            return self.server[2]

    @property
    def port(self):
        if isinstance(self.server, tuple):
            return self.server[3]

    @property
    def address(self):
        return "{}://{}:{}".format(self.protocol, self.interface, self.port)

    @property
    def socket_closed(self):
        return self.socket.closed if hasattr(self, 'socket') else True

    @property
    def pipe_closed(self):
        return self.pipe.closed if hasattr(self, 'pipe') else True

    @property
    def started(self):
        return not self._stop_event.is_set()

    def do_close(self):
        pass

    def do_recv(self, sock):
        return sock.recv_multipart(zmq.DONTWAIT)

    def do_send(self, sock, message):
        return sock.send_multipart(message)

    def read_write(self, timeout=None):
        t_ms = timeout * 1000 if timeout else None
        while not self._shutdown_request:
            try:
                socks = dict(self.poller.poll(t_ms))
                if socks.get(self.socket) == zmq.POLLIN:
                    message = self.do_recv(self.socket)
                    # print "in message", message
                    self.do_send(self.pipe, message)
                if socks.get(self.pipe) == zmq.POLLIN:
                    message = self.do_recv(self.pipe)
                    # print "out message", message
                    self.do_send(self.socket, message)
            except:
                self.do_close()
                self.stop()
                raise

    def _serve(self):
        self._stop_event.clear()
        try:
            self.read_write()
        except:
            self._stop()
            raise

    def _init_socket(self, linger=1, hwm_size=100, identity=uuid.uuid4()):
        self.socket = self.context.socket(self.pattern)
        self.socket.linger = linger
        self.socket.set_hwm(hwm_size)
        self.socket.setsockopt_unicode(zmq.IDENTITY, unicode(identity))
        self.socket.bind(self.address)
        self.poller.register(self.socket, zmq.POLLIN)

    def _init_pipe(self, linger=1, hwm_size=100, identity=uuid.uuid4()):
        self.pipe_endpoint = "inproc://{0}.inproc".format(id(self))
        self.pipe = self.context.socket(zmq.PAIR)
        self.pipe.linger = linger
        self.pipe.bind(self.pipe_endpoint)
        self.poller.register(self.pipe, zmq.POLLIN)

    def _init_handler_thread(self):
        ht = ZMQRequestHandlerThread(self.RequestHandlerClass,
                                     self.context,
                                     self.ppoller,
                                     self.pipe_endpoint,
        )
        ht.start()

    def _start(self):
        self._init_socket()
        self._init_pipe()
        self._init_handler_thread()
        self._serve()

    def start(self):
        Thread(target=self._start).start()

    def _close_socket(self):
        if not self.socket_closed:
            self.socket.close()
            self.poller.unregister(self.socket)

    def _close_pipe(self):
        if not self.pipe_closed:
            self.pipe.close()
            self.poller.unregister(self.pipe)

    def _stop(self):
        self._shutdown_request = True
        self._stop_event.set()
        self._close_socket()
        self._close_pipe()

    def stop(self):
        st = Thread(target=self._stop)
        st.start()
        st.join()

    def serve(self):
        try:
            self._start()
            self._stop_event.wait()
        finally:
            self.stop()

    def _formatinfo(self):
        result = ''
        return result

    def __repr__(self):
        return '<%s at %s %s>' % (type(self).__name__, hex(id(self)), self._formatinfo())

    def __str__(self):
        return '<%s %s>' % (type(self).__name__, self._formatinfo())
