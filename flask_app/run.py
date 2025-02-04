from app.__init__ import create_app
from flask import Flask

app, socketio = create_app()
if type(app) == Flask:
    socketio.run(app, debug=True, host='0.0.0.0')
else:
    print('App is not a Flask instance')