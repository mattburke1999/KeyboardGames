from app.routes import app
from app.games.sockets import socketio
from app.auth.routes import bp as auth_bp
from app.games.routes import bp as games_bp
from app.skins.routes import bp as skins_bp
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv(override=True)

def create_app():
    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(skins_bp)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    return app, socketio