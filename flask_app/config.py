from dotenv import load_dotenv
load_dotenv(override=True)
import os

FLASK_ENV = os.environ.get('FLASK_ENV')

class Config():
    DB_CNXN = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    
class TestConfig(Config):
    DEBUG = True
    DB_CNXN = os.getenv('TEST_DATABASE_URL')
    
class ProdConfig(Config):
    DEBUG = False
    DB_CNXN = os.getenv('DATABASE_URL')