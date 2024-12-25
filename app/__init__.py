from routes import app
from dotenv import load_dotenv
import os
load_dotenv(override=True)

def create_app():
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    return app