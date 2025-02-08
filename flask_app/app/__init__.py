from app.routes import app
from app.games.sockets import socketio
from app.data_access.db import BaseDB
from app.data_access.redis_store import Redis_Store
from app.auth.routes import bp as auth_bp
from app.games.routes import bp as games_bp
from app.skins.routes import bp as skins_bp
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv(override=True)

def create_app():
    BaseDB.initialize_pool(db_str=os.environ['DATABASE_URL'], minconn=1, maxconn=10)
    Redis_Store.initialize(host='localhost', port=6379, password=os.getenv('REDIS_PASSWORD'))
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(skins_bp)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    return app, socketio