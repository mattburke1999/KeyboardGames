from unit_tests import BaseTestClass
import unittest
from app import create_app

class TestGames(BaseTestClass):
    
    def test_sample(self):
        self.assertEqual(1, 1)
        
if __name__ == '__main__':
    unittest.main()