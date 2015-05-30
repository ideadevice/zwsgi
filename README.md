# ZWSGI
ZeroMQ <-> WSGI Bridge.

ZWSGI provides the ability to use rich messaging patterns provided by ZeroMQ to your existing WSGI applications. ZWSGI seamlessly changes the underlying transport layer from HTTP to [ZHTTP](http://rfc.zeromq.org/spec:33 "ZHTTP"). It is built on top of [pyzmq] (https://github.com/zeromq/pyzmq "pyzmq")

## Example:

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
