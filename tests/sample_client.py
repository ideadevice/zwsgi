# -*- coding: utf-8 -*-

import uuid

import zmq
import ujson as json

def client(pattern=zmq.DEALER, addr='tcp://localhost:7000'):
    c = zmq.Context()
    sock = c.socket(pattern)
    sock.connect(addr)
    return sock


def run(sock, req='hello world'):

    # sock.setsockopt_string(zmq.IDENTITY, u'fancy client'),

    req = {
        'from': sock.getsockopt_string(zmq.IDENTITY),
        'id': "%s" % uuid.uuid4(),
        'type': 'data',
        'method': 'GET',
        'uri': '/ping?a=b&c=d',
        'auth': ('username', 'passwd'),
        'headers': {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        },
        'body': 'sample body',
        'user-data': 'test client',
    }

    request = json.dumps(req)
    sock.send(request)
    print sock.recv_multipart()



def main():
    sock = client()
    run(sock)

if __name__ == '__main__':
    main()
