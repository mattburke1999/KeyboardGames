from routes import app
from sockets import socketio
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv(override=True)

def create_app():
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    return app, socketio