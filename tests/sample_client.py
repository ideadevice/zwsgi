# -*- coding: utf-8 -*-

import zmq

def client(pattern=zmq.REQ, addr='tcp://localhost:7000'):
    c = zmq.Context()
    sock = c.socket(pattern)
    sock.connect(addr)
    return sock


def run(sock, req='hello world'):
    sock.send(req)
    return sock.recv()


def main():
    sock = client()
    print run(sock)

if __name__ == '__main__':
    main()
