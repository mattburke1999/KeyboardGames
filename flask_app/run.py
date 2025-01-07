from __init__ import create_app
from flask import Flask

app = create_app()
if type(app) == Flask:
    app.run(debug=True, host='0.0.0.0')
else:
    print('App is not a Flask instance')