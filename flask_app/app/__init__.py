from .routes import app
from .games.sockets import socketio
from .data_access.db import BaseDB
from .data_access.redis_store import Redis_Store
from .auth.routes import bp as auth_bp
from .games.routes import bp as games_bp
from .skins.routes import bp as skins_bp
from flask_cors import CORS
from config import Config
from config import ProdConfig
from config import TestConfig
from config import FLASK_ENV

def create_app():
        
    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(skins_bp)
    app.secret_key = Config.SECRET_KEY
    
    if FLASK_ENV == 'production':
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(TestConfig)
        
    print(app.config['DB_CNXN'])
        
    BaseDB.initialize_pool(db_str=app.config['DB_CNXN'], minconn=1, maxconn=10)
    Redis_Store.initialize(host='localhost', port=6379, password=app.config['DB_CNXN'])
    
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    return app, socketio