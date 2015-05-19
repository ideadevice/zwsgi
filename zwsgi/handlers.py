# -*- coding: utf-8 -*-

import os
import sys
import traceback
import urlparse
import base64
from StringIO import StringIO

import zmq
import ujson as json


class ZMQBaseRequestHandler(object):

    def __init__(self, request_str, application, channel):
        self.request_str = request_str
        self.application = application
        self.channel = channel
        self.response = {}

    def decode_request(self):
        self.request = json.loads(self.request_str)

    def encode_response(self):
        self.response_str = json.dumps(self.response)

    def send_response(self):
        return self.response_str

    def _handle(self):
        self.response = self.request

    def handle(self):
        self.decode_request()
        self._handle()
        self.encode_response()
        return self.send_response()


class ZMQWSGIRequestHandler(ZMQBaseRequestHandler):

    base_env = {
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'GATEWAY_INTERFACE': 'CGI/1.1',
        'SERVER_SOFTWARE': 'zmq/%d.%d.%d Python/%d.%d' % (zmq.zmq_version_info() + sys.version_info[:2]),
        'SCRIPT_NAME': '',
        'QUERY_STRING': '',
        'QUERY_PARAMS': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '',
        'wsgi.version': (1, 0),
        'wsgi.multithread': True,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.url_scheme': 'zhttp',
        'wsgi.errors': StringIO(),
    }

    def __init__(self, request_str, application, channel, env_update=None):
        super(ZMQWSGIRequestHandler, self).__init__(request_str, application, channel)

        self.env = self.base_env.copy()
        if env_update:
            self.env.update(env_update)

    def get_environ(self):
        return self.env.copy()

    def make_environ(self):

        # Method
        self.env['REQUEST_METHOD'] = self.request.get('method')

        # Headers
        headers = self.request.get('headers')
        if headers:
            for k,v in headers.iteritems():
                self.env[k] = headers.get(k, '')

        # Client
        self.env['REMOTE_ADDR'] = self.request.get('from')

        # URL
        parse = urlparse.urlparse(self.request.get('uri'))
        self.env['PATH_INFO'] = parse.path
        self.env['QUERY_STRING'] = parse.query

        # Body
        body = self.request.get('body')
        self.env['wsgi.input'] = StringIO(body)

        # AUTH
        auth = self.request.get('auth')
        if auth:
            token = base64.encodestring('%s:%s' % (auth[0], auth[1]))
            self.env['HTTP_AUTHORIZATION'] = 'Basic %s' % token

        # Channel
        self.env['channel'] = self.channel

    def start_response(self, status, headers, exc_info=None):
        self.response['headers'] = headers
        self.response['code'] = int(status.split()[0])
        self.response['reason'] = status

    def start_application(self):
        result = None
        try:
            result = self.application(self.env, self.start_response)
            outfile = StringIO()
            for data in result:
                outfile.write(data)
        except:
            raise
        finally:
            if hasattr(result, 'close'):
                result.close()
        self.response['body'] = outfile.getvalue()

    def _handle(self):
        print "Make environ", os.getpid()
        self.make_environ()
        print "Start Application"
        self.start_application()

    def log_error(self, msg, *args):
        try:
            message = msg % args
        except Exception:
            traceback.print_exc()
            message = '%r %r' % (msg, args)
        try:
            message = '%s' % (message)
        except Exception:
            pass
        try:
            sys.stderr.write(message + '\n')
        except Exception:
            traceback.print_exc()
