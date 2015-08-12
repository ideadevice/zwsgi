# -*- coding: utf-8 -*-

"""Base ZMQ server classes.
"""

import os
from threading import Thread
from multiprocessing import Process
import sys

import zmq
from zmq.error import ZMQError

from zwsgi.handlers import ZMQWSGIRequestHandler
from zwsgi.monkey import _Poller


class ZMQBaseServerChannel(object):

    pattern = zmq.PUSH

    def __init__(self, ingress, context, address, RequestHandlerClass, app):
        super(ZMQBaseServerChannel, self).__init__()
        self.context = context or zmq.Context()
        self.ingress = ingress
        self.address = address
        self.RequestHandlerClass = RequestHandlerClass
        self.app = app

    def connect(self):
        self.sock = self.context.socket(self.pattern)
        self.sock.linger = 1
        self.sock.connect(self.address)

    def unpack(self):
        return self.ingress

    def handle(self, request):
        # import time; time.sleep(0.1)
        return self.RequestHandlerClass(request, self.app, self).handle()

    def pack(self, response, more):
        self.egress = [response,] + [more,]

    def send(self):
        self.sock.send_multipart(self.egress)

    def disconnect(self):
        self.sock.close()

    def send_response(self, response, more="1"):
        self.pack(response, more)
        self.send()

    def run(self):
        # report_fds("    {} 0".format(self.name))
        self.connect()
        # report_fds("    {} 1".format(self.name))
        # print "Ingress:", self.ingress
        request = self.unpack()
        # report_fds("    {} 2".format(self.name))
        # print "Request:", request
        response = self.handle(request)
        # report_fds("    {} 3".format(self.name))
        # print "Response:", response
        self.send_response(response, more="0")
        # report_fds("    {} 4".format(self.name))
        self.disconnect()
        # report_fds("    {} 5".format(self.name))


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
    Channel = ZMQBaseServerChannel
    RequestHandlerClass = ZMQWSGIRequestHandler
    pattern = None
    pipe_pattern = PULL
    poller = _Poller()

    def __init__(self, listener, app,
                 context=None, bind=True,
                 spawn_type=Thread, spawn_size=2,
                 handler_class=None):
        if isinstance(listener, tuple):
            self.address = "{}://{}:{}".format(self.protocol, self.listener[0], self.listener[1])
            self.bound = False
            self.sock = self.context.socket(self.pattern)
        elif isinstance(listener, zmq.Socket):
            self.sock = listener
            self.address = self.sock.getsockopt(zmq.LAST_ENDPOINT)
            self.bound = True
        self.app = app
        self.context = context or zmq.Context.instance()
        self.pipe = self.context.socket(self.pipe_pattern)
        if handler_class is not None:
            self.RequestHandlerClass = handler_class
        self.bind = bind
        self.application = app
        self.spawn_type = spawn_type
        self.spawn_size = spawn_size
        self.pool = self._pool()
        self._shutdown_request = False


    @property
    def sock_closed(self):
        return self.sock.closed if hasattr(self, 'sock') else True

    @property
    def pipe_closed(self):
        return self.pipe.closed if hasattr(self, 'pipe') else True

    def do_close(self):
        pass

    def start_channel(self, ingress, name):
        self.Channel(ingress, self.channel_context, self.pipe_address,
                     self.RequestHandlerClass, self.app, name).run()

    def _pool(self):
        while self.spawn_size > 0:
            self.spawn_size -= 1
            yield self.spawn_type

    def _handle(self, ingress):
        # print "pool size", self.spawn_size
        # report_fds("  Before")
        if self.spawn_size > 0:
            next(self.pool)(target=self.start_channel, args=(ingress, self.spawn_size)).start()
            # report_fds("  After")
        else:
            # TODO: Send ZHTTP response
            ingress[-1] = "Server capacity reached"
            self.sock.send_multipart(ingress)

    def _accept_pipe(self):
        if self.spawn_type is Thread:
            self.channel_context = self.context
            self.pipe_address = "inproc://inproc_{}".format(id(self))
        elif self.spawn_type is Process:
            self.channel_context = None
            self.pipe_address = "ipc:///tmp/ipc_{}".format(id(self))
        else:
            print >> sys.stderr, "Unknown pool type"
            sys.exit(-1)
        self.pipe.bind(self.pipe_address)

    def _accept_sock(self):
        if not self.bound:
            self.sock.bind(self.address) if self.bind else self.sock.connect(self.address)

    def _register_socks(self):
        self.poller.register(self.sock, zmq.POLLIN)
        self.poller.register(self.pipe, zmq.POLLIN)

    def _accept(self):
        self._accept_sock()
        self._accept_pipe()
        self._register_socks()

    def _pre_accept(self):
        pass

    def _start_accept(self):
        self._pre_accept()
        self._accept()
        self._post_accept()

    def _post_accept(self):
        pass

    def _eventloop(self):
        print "Starting Server", os.getpid()
        while not self._shutdown_request:
            try:
                events = dict(self.poller.poll())
                # print "Events", events
                if self.sock in events:
                    # report_fds("Before handling")
                    data = self.sock.recv_multipart(zmq.DONTWAIT)
                    self.pipe.send_multipart(data)
                    # report_fds("After handling")
                if self.pipe in events:
                    egress = self.pipe.recv_multipart(zmq.DONTWAIT)
                    # print "egress", egress
                    self.sock.send_multipart(egress[1:])
                    if egress[0] == "0":
                        # print "Channel completed execution"
                        self.spawn_size += 1
                        # print "Pool size", self.spawn_size
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


class ZMQPreforkedWorkerChannel(object):
    pattern = zmq.ROUTER

    def __init__(self, context, address, RequestHandlerClass, app):
        # super(ZMQBaseServerChannel, self).__init__()
        self.context = context or zmq.Context.instance()
        self.address = address
        self.RequestHandlerClass = RequestHandlerClass
        self.app = app

        self.sock = self.context.socket(self.pattern)
        self.sock.linger = 1
        self.sock.connect(self.address)

        self.stop = False
    
    def handle(self, request):
        # import time; time.sleep(0.1)
        return self.RequestHandlerClass(request, self.app, self).handle()

    def run(self):
        while not self.stop:
            try:
                request = self.sock.recv_multipart()
                # print "Got {}".format(request)
                # We will have two addresses now. The incoming packet will look like this
                # [pipe_router_identity, client_router_identity, '' , actual_command]
                # We need to use just -1 for command processing and then retain the envelope from 1: 
                # while sending this back.
                pipe_identity, envelope, command = request[0], request[1:-1], request[-1]
                command = request[-1]
                command_response = self.handle(command)
                response = [pipe_identity, ''] + envelope + [command_response]
                # print "Returning {}".format(response)
                self.sock.send_multipart(response)
            except zmq.error.Again as e:
                pass

    def terminate(self):
        self.stop = True


class ZMQPreforkedServer(ZMQBaseServer):
    pipe_pattern = zmq.DEALER
    Channel = ZMQPreforkedWorkerChannel
    RequestHandlerClass = ZMQWSGIRequestHandler

    def __init__(self, address, command_handler, handler_class, spawn_type, spawn_size):
        super(ZMQPreforkedServer, self).__init__(address, command_handler, 
                                                 spawn_type = spawn_type, 
                                                 spawn_size = spawn_size,
                                                 handler_class = handler_class)
        self.workers = []
        self._start_accept()
        self.prepare_worker_pool()

    def prepare_worker_pool(self):
        sys.stdout.write("Pre spawning workers ")
        i = 0
        for i in range(self.spawn_size):
            sys.stdout.write(".")
            sys.stdout.flush()
            worker_channel = self.Channel(self.context, self.pipe_address, self.RequestHandlerClass, self.app)
            worker = self.spawn_type(target=worker_channel.run)
            worker.start()
            self.workers.append(worker_channel)
        print "({})".format(i+1)


    def _eventloop(self):
        print "Starting Server", os.getpid()
        while not self._shutdown_request:
            events = dict(self.poller.poll())
            # print "Events", events
            if self.sock in events:
                # report_fds("Before handling")
                data = self.sock.recv_multipart(zmq.DONTWAIT)
                # print "From client .. {}".format(data)
                self.pipe.send_multipart(data)
                # print " Sent it to a worker".format(data)
                # report_fds("After handling")
            if self.pipe in events:
                egress = self.pipe.recv_multipart(zmq.DONTWAIT)
                # print "From pipe {}".format(egress)
                # print "egress", egress
                self.sock.send_multipart(egress[1:])
                # print " Sent it to client"

    def _serve(self):
        self._eventloop()

    def terminate(self):
        for i in self.workers:
            i.terminate()
        self._stop()
        
