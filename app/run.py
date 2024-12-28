from __init__ import create_app
from sockets import socketio
from flask import Flask

app = create_app()
if type(app) == Flask:
    socketio.run(app, debug=True, host='0.0.0.0')
else:
    print('App is not a Flask instance')