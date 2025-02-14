import unittest
import psycopg2 as pg
import os
from app import create_app

class BaseTestClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test client."""
        cls.app, cls.socketio = create_app(config='test')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
    def tearDownClass(cls):
        """Tear down app context."""
        cls.app_context.pop()
    
    @classmethod
    def connect_db(cls):
        return pg.connect(os.getenv('TEST_DATABASE_URL'))