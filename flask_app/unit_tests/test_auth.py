import unittest
from unittest.mock import patch
from app.auth.services import create_user
from app.auth.services import try_login
from app.auth.services import check_unique_register_input
from . import BaseTest
import random
  

class Test_try_login(BaseTest):
    
    def setUp(self):
        super().setUp()
    
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
                self.assertTrue(result.success)
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
    def test_wrong_creds(self, mock_bcrypt, mock_DB):
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
                
                data = {'username': 'test', 'password': f'wrong{password}'}
                
                # act
                result = try_login(data)
                
                # assert
                if not result.success:
                    if 'error' in result.result:
                        print(result.result['error'])
                    raise Exception('try_login() failed')
                self.assertTrue(result.success)
                self.assertIn('logged_in', result.result)
                self.assertFalse(result.result['logged_in'])
                # assert mock_sesion was not called/set
                mock_session.__setitem__.assert_not_called()
                mock_session.__getitem__.assert_not_called()
                
    @patch('app.auth.services.DB.check_user')
    @patch('app.auth.services.bcrypt.checkpw')
    def test_db_exception(self, mock_bcrypt, mock_DB):
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
    def test_missing_fields(self, mock_bcrypt, mock_DB):
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
                if not result.success:
                    if 'error' in result.result:
                        print(result.result['error'])
                    raise Exception('try_login() failed')
                self.assertTrue(result.success)
                self.assertIn('error', result.result)
                mock_bcrypt.assert_not_called()
                mock_DB.assert_not_called()
                mock_session.__setitem__.assert_not_called()
                mock_session.__getitem__.assert_not_called()
                
class Test_create_user(BaseTest):
    
    def setUp(self):
        super().setUp()
    
    @patch('app.auth.services.DB')
    def test_missing_fields(self, mock_DB):
        with self.app.test_request_context():
            with patch('app.auth.services.session') as mock_session:
                # arrange
                data = {'first_name': '', 'last_name': '', 'username': '', 'email': '', 'password': ''}
                
                # act
                result = create_user(data)
                
                # assert
                if not result.success:
                    if 'error' in result.result:
                        print(result.result['error'])
                    raise Exception('create_user() failed')
                self.assertTrue(result.success)
                self.assertIn('registered', result.result)
                self.assertFalse(result.result['registered'])
                self.assertIn('error', result.result)
                self.assertEqual(result.result['error'], 'Missing required fields')
                mock_DB.connect_db.assert_not_called()
                mock_DB.create_user.assert_not_called()
                mock_DB.add_default_skin.assert_not_called()
                mock_session.__setitem__.assert_not_called()
                mock_session.__getitem__.assert_not_called()
    
    @patch('app.auth.services.DB')
    def test_create_user_success(self, mock_DB):
        with self.app.test_request_context():
            with patch('app.auth.services.session') as mock_session:
                # arrange
                data = {'first_name': 'test', 'last_name': 'test', 'username': 'test', 'email': 'test', 'password': 'test'}
                user_id = 1
                mock_DB.create_user.return_value = user_id
                mock_DB.add_default_skin.return_value = None
                mock_DB.connect_db.return_value = yield self.mock_connection
                
                mock_session.__getitem__.side_effect = self.mock_session_get
                mock_session.__setitem__.side_effect = self.mock_session_set
                
                # act
                result = create_user(data)
                
                # assert
                if not result.success:
                    if 'error' in result.result:
                        print(result.result['error'])
                    raise Exception('create_user() failed')
                self.assertTrue(result.success)
                self.assertIn('registered', result.result)
                self.assertTrue(result.result['registered'])
                self.assertIn('logged_in', self.mock_session)
                self.assertTrue(mock_session['logged_in'])
                self.assertIn('user_id', self.mock_session)
                self.assertEqual(mock_session['user_id'], user_id)
                self.mock_connection.commit.assert_called()
                self.mock_connection.rollback.assert_not_called()
                
    @patch('app.auth.services.DB')
    def test_db_exception(self, mock_DB):
        with self.app.test_request_context():
            with patch('app.auth.services.session') as mock_session:
                # arrange
                data = {'first_name': 'test', 'last_name': 'test', 'username': 'test', 'email': 'test', 'password': 'test'}
                mock_DB.create_user.side_effect = Exception('DB error')
                mock_DB.add_default_skin.return_value = None
                mock_DB.connect_db.return_value = yield self.mock_connection
                
                mock_session.__getitem__.side_effect = self.mock_session_get
                mock_session.__setitem__.side_effect = self.mock_session_set
                
                # act
                result = create_user(data)
                
                # assert
                self.assertFalse(result.success)
                self.assertIn('error', result.result)
                self.mock_connection.commit.assert_not_called()
                self.mock_connection.rollback.assert_called()
                self.assertIn('logged_in', self.mock_session)
                self.assertFalse(mock_session['logged_in'])
                self.assertIn('user_id', self.mock_session)
                self.assertIsNone(mock_session['user_id'])

class Test_check_unique_register_input(BaseTest):
    
    def setUp(self):
        super().setUp()
    
    @patch('app.auth.services.DB.check_unique_register_input')
    def test_unique_username_success(self, mock_DB):
        # arrange
        input_type = 'username'
        data = {'username': 'test'}
        unique = random.choice([True, False])
        mock_DB.return_value = unique
        
        # act
        result = check_unique_register_input(input_type, data)
        
        # assert
        self.assertTrue(result.success)
        self.assertIn('unique', result.result)
        self.assertEqual(result.result['unique'], unique)
        mock_DB.assert_called()
    
    @patch('app.auth.services.DB.check_unique_register_input')
    def test_incorrect_input_type(self, mock_DB):
        # arrange
        input_type = 'incorrect'
        data = {'username': 'test'}
        mock_DB.return_value = None
        
        # act
        result = check_unique_register_input(input_type, data) # type: ignore
        
        # assert
        self.assertTrue(result.success)
        self.assertIn('error', result.result)
        self.assertEqual(result.result['error'], 'Invalid input type')
        
    @patch('app.auth.services.DB.check_unique_register_input')
    def test_db_exception(self, mock_DB):
        # arrange
        input_type = 'username'
        data = {'username': 'test'}
        mock_DB.side_effect = Exception('DB error')
        
        # act
        result = check_unique_register_input(input_type, data)
        
        # assert
        self.assertFalse(result.success)
        self.assertIn('error', result.result)

if __name__ == '__main__':
    unittest.main()