import pytest
import json
from utils.jwt_utils import JWTUtils


class TestAuthRoutes:
    def test_register_success(self, client):
        response = client.post('/api/auth/register', json={
            'fullname': 'New User',
            'email': 'newuser@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['success'] is True
        assert data['message'] == 'User created successfully'
        assert data['user']['email'] == 'newuser@test.com'
        assert data['user']['role'] == 'user'
        assert 'token' in data
        assert data['token_type'] == 'Bearer'
        
        assert 'password' not in data['user']
    
    def test_register_role_enforcement(self, client):
        response = client.post('/api/auth/register', json={
            'fullname': 'Admin Attempt',
            'email': 'adminattempt@test.com',
            'password': 'password123',
            'role': 'admin'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['success'] is True
        assert data['user']['role'] == 'user'
    
    def test_register_missing_fields(self, client):
        response = client.post('/api/auth/register', json={
            'email': 'missing@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'required' in data['message'].lower()
        
        response = client.post('/api/auth/register', json={
            'fullname': 'Missing Email',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        
        response = client.post('/api/auth/register', json={
            'fullname': 'Missing Password',
            'email': 'missingpwd@test.com'
        })
        
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client):
        client.post('/api/auth/register', json={
            'fullname': 'First User',
            'email': 'duplicate@test.com',
            'password': 'password123'
        })
        
        response = client.post('/api/auth/register', json={
            'fullname': 'Second User',
            'email': 'duplicate@test.com',
            'password': 'password456'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'already in use' in data['message']
    
    def test_login_success(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'user123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['message'] == 'Login successful'
        assert data['user']['email'] == 'user@test.com'
        assert 'token' in data
        assert data['token_type'] == 'Bearer'
    
    def test_login_wrong_password(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'incorrect' in data['message'].lower()
        assert data['user'] is None
    
    def test_login_nonexistent_user(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'incorrect' in data['message'].lower()
    
    def test_login_missing_credentials(self, client):
        response = client.post('/api/auth/login', json={
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'required' in data['message'].lower()
        
        response = client.post('/api/auth/login', json={
            'email': 'user@test.com'
        })
        
        assert response.status_code == 400
    
    def test_get_profile_success(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.get('/api/auth/profile', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['user']['email'] == 'user@test.com'
        assert 'password' not in data['user']
    
    def test_get_profile_no_token(self, client):
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'missing' in data['message'].lower()
    
    def test_get_profile_invalid_token(self, client):
        headers = {'Authorization': 'Bearer invalid.token.here'}
        
        response = client.get('/api/auth/profile', headers=headers)
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid token' in data['message']
    
    def test_change_password_success(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.put('/api/auth/change-password', 
            headers=headers,
            json={
                'current_password': 'user123',
                'new_password': 'newpassword123'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'successfully' in data['message'].lower()
        
        login_response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'user123'
        })
        assert login_response.status_code == 401
        
        login_response = client.post('/api/auth/login', json={
            'email': 'user@test.com',
            'password': 'newpassword123'
        })
        assert login_response.status_code == 200
    
    def test_change_password_wrong_current(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.put('/api/auth/change-password',
            headers=headers,
            json={
                'current_password': 'wrongpassword',
                'new_password': 'newpassword123'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'incorrect' in data['message'].lower()
    
    def test_change_password_missing_fields(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.put('/api/auth/change-password',
            headers=headers,
            json={
                'new_password': 'newpassword123'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'required' in data['message'].lower()
    
    def test_change_password_no_token(self, client):
        response = client.put('/api/auth/change-password', json={
            'current_password': 'user123',
            'new_password': 'newpassword123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'missing' in data['message'].lower()
    
    def test_refresh_token_success(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.post('/api/auth/refresh', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'refreshed' in data['message'].lower()
        assert 'token' in data
        assert data['token_type'] == 'Bearer'
    
    def test_refresh_token_no_token(self, client):
        response = client.post('/api/auth/refresh')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'missing' in data['message'].lower()
    
    def test_refresh_token_invalid(self, client):
        headers = {'Authorization': 'Bearer invalid.token.here'}
        
        response = client.post('/api/auth/refresh', headers=headers)
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    def test_verify_token_success(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.post('/api/auth/verify', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'valid' in data['message'].lower()
        assert 'user_data' in data
        assert data['user_data']['email'] == 'user@test.com'
    
    def test_verify_token_invalid(self, client):
        headers = {'Authorization': 'Bearer invalid.token.here'}
        
        response = client.post('/api/auth/verify', headers=headers)
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid token' in data['message']
    
    def test_verify_token_no_token(self, client):
        response = client.post('/api/auth/verify')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'missing' in data['message'].lower()
    
    def test_invalid_authorization_header_format(self, client):
        headers = {'Authorization': 'token.here'}
        
        endpoints = [
            '/api/auth/profile',
            '/api/auth/refresh',
            '/api/auth/verify'
        ]
        
        for endpoint in endpoints:
            if endpoint == '/api/auth/profile':
                response = client.get(endpoint, headers=headers)
            else:
                response = client.post(endpoint, headers=headers)
            
            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False
            assert 'format' in data['message'].lower()
    
    def test_token_contains_correct_user_data(self, client):
        register_response = client.post('/api/auth/register', json={
            'fullname': 'Token Test User',
            'email': 'tokentest@test.com',
            'password': 'password123'
        })
        
        assert register_response.status_code == 201
        data = register_response.get_json()
        token = data['token']
        
        with client.application.app_context():
            user_data = JWTUtils.get_user_from_token(token)
            
            assert user_data is not None
            assert user_data['email'] == 'tokentest@test.com'
            assert user_data['role'] == 'user'
            assert user_data['user_id'] == data['user']['id'] 