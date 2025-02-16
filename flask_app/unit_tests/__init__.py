from flask import Flask
import unittest
from unittest.mock import MagicMock


class BaseTest(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask('test')
        self.mock_session = {}
        self.mock_connection = MagicMock()
        
    def mock_session_get(self, key):
        return self.mock_session[key]
    
    def mock_session_set(self, key, value):
        self.mock_session[key] = value