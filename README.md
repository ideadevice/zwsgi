# ZWSGI
ZeroMQ <-> WSGI Bridge.

ZWSGI provides the ability to use rich messaging patterns provided by ZeroMQ to your existing WSGI applications. It changes the underlying transport layer from HTTP to [ZHTTP](http://rfc.zeromq.org/spec:33 "ZHTTP"). It is built on top of [pyzmq] (https://github.com/zeromq/pyzmq "pyzmq") bindings and can be configured to use threads, [greenlets](https://github.com/gevent/gevent "gevent") or processes to handle incoming requests.

## Sample Use Case

ZWSGI can be used to realize advanced ZeroMQ patterns like [MDP] (http://rfc.zeromq.org/spec:7 "MDP"), where workers are ZWSGI applications that connect to a broker. This provides a way to build a scalable microservices based service oriented architecture.

## Examples

### Sample Flask App (Threads).

```python
from flask import Flask
from zwsgi.servers import ZMQRouterDealerServer as WSGIServer


@app.route('/ping')
def hello_world():
    return 'Hello World!'


app = Flask(__name__)
server = WSGIServer(('127.0.0.1', 7000), app)
server.serve_forever()
```

### Sample Flask App (Gevent).

```python
from flask import Flask
from zwsgi import monkey
monkey.patch_all()
from zwsgi.servers import ZMQRouterDealerServer as WSGIServer


@app.route('/ping')
def hello_world():
    return 'Hello World!'


app = Flask(__name__)
server = WSGIServer(('127.0.0.1', 7000), app)
server.serve_forever()
```

### Sample Flask App (MultiProcess).

```python
from flask import Flask
from multiprocessing import Process
from zwsgi.servers import ZMQRouterDealerServer as WSGIServer


@app.route('/ping')
def hello_world():
    return 'Hello World!'


app = Flask(__name__)
server = WSGIServer(('127.0.0.1', 7000), app, spawn_type=Process)
server.serve_forever()
```