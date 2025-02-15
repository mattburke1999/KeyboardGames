import unittest
from flask import Flask
from unittest.mock import patch
from app.auth.services import create_user
from app.auth.services import try_login
import random

class Test_try_login(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask('test')
        self.mock_session = {}
        
    def mock_session_get(self, key):
        return self.mock_session[key]
    
    def mock_session_set(self, key, value):
        self.mock_session[key] = value
    
    @patch('app.auth.services.DB.check_user')
    @patch('app.auth.services.bcrypt.checkpw')
    def test_login_success(self, mock_bcrypt, mock_DB):
        with self.app.test_request_context():  # Provides a request context
            with patch('app.auth.services.session') as mock_session:
                # arrange
                user_id = 1
                password = 'test'
                byte_password = bytes(password, 'utf-8')
                is_admin = random.choice([True, False])
                mock_DB.return_value = (user_id, byte_password, is_admin)
                mock_bcrypt.return_value = True
                
                mock_session.__getitem__.side_effect = self.mock_session_get
                mock_session.__setitem__.side_effect = self.mock_session_set
                
                data = {'username': 'test', 'password': password}
                
                # act
                result = try_login(data)
                    
                # assert
                if not result.success:
                    if 'error' in result.result:
                        print(result.result['error'])
                    raise Exception('try_login() failed')
                self.assertIn('logged_in', result.result)
                self.assertTrue(result.result['logged_in'])
                self.assertIn('logged_in', self.mock_session)
                self.assertTrue(mock_session['logged_in'])
                self.assertIn('user_id', self.mock_session)
                self.assertEqual(mock_session['user_id'], user_id)
                self.assertIn('is_admin', self.mock_session)
                self.assertEqual(mock_session['is_admin'], is_admin)
                
    @patch('app.auth.services.DB.check_user')
    @patch('app.auth.services.bcrypt.checkpw')
    def test_login_failure(self, mock_bcrypt, mock_DB):
        with self.app.test_request_context():
            with patch('app.auth.services.session') as mock_session:
                # arrange
                user_id = 1
                password = 'test'
                byte_password = bytes(password, 'utf-8')
                is_admin = random.choice([True, False])
                mock_DB.return_value = (user_id, byte_password, is_admin)
                mock_bcrypt.return_value = False
                
                mock_session.__getitem__.side_effect = self.mock_session_get
                mock_session.__setitem__.side_effect = self.mock_session_set
                
                data = {'username': 'test', 'password': password}
                
                # act
                result = try_login(data)
                
                # assert
                if not result.success:
                    if 'error' in result.result:
                        print(result.result['error'])
                    raise Exception('try_login() failed')
                self.assertIn('logged_in', result.result)
                self.assertFalse(result.result['logged_in'])
                # assert mock_sesion was not called/set
                mock_session.__setitem__.assert_not_called()
                mock_session.__getitem__.assert_not_called()
                
    @patch('app.auth.services.DB.check_user')
    @patch('app.auth.services.bcrypt.checkpw')
    def test_login_db_exception(self, mock_bcrypt, mock_DB):
        with self.app.test_request_context():
            with patch('app.auth.services.session') as mock_session:
                # arrange
                user_id = 1
                password = 'test'
                mock_DB.side_effect = Exception('DB error')
                
                mock_session.__getitem__.side_effect = self.mock_session_get
                mock_session.__setitem__.side_effect = self.mock_session_set
                
                data = {'username': 'test', 'password': password}
                
                # act
                result = try_login(data)
                
                # assert
                self.assertFalse(result.success)
                self.assertIn('error', result.result)
                mock_bcrypt.assert_not_called()
                mock_session.__setitem__.assert_not_called()
                mock_session.__getitem__.assert_not_called()
    
    @patch('app.auth.services.DB.check_user')
    @patch('app.auth.services.bcrypt.checkpw')
    def test_login_incorrect_input(self, mock_bcrypt, mock_DB):
        with self.app.test_request_context():
            with patch('app.auth.services.session') as mock_session:
                # arrange
                user_id = 1
                password = 'test'
                mock_DB.return_value = (user_id, password, False)
                
                mock_session.__getitem__.side_effect = self.mock_session_get
                mock_session.__setitem__.side_effect = self.mock_session_set
                
                data = {'username': '', 'password': ''}
                
                # act
                result = try_login(data)
                
                # assert
                self.assertFalse(result.success)
                self.assertIn('error', result.result)
                mock_bcrypt.assert_not_called()
                mock_DB.assert_not_called()
                mock_session.__setitem__.assert_not_called()
                mock_session.__getitem__.assert_not_called()
                
        
if __name__ == '__main__':
    unittest.main()