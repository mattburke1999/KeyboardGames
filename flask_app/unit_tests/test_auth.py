import unittest
from app.auth.services import create_user
from app.auth.services import try_login
from app.auth.services import bcrypt

class TestAuth(unittest.TestCase):
    
    def test_login_success(self):
        # arrange
        pass
        
        
if __name__ == '__main__':
    unittest.main()