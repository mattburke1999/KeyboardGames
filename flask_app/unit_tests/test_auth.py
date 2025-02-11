from unit_tests import BaseTestClass
import unittest
from app import create_app
from app.auth.services import create_user

class TestAuth(BaseTestClass):
    
    def test_sample(self):
        self.assertEqual(1, 1)

    def test_sample2(self):
        self.assertEqual(2, 1)
        
if __name__ == '__main__':
    unittest.main()