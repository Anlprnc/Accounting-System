import pytest
import jwt
from datetime import datetime, timedelta
from utils.jwt_utils import JWTUtils
from flask import Flask


class TestJWTUtils:
    def test_generate_token_success(self, app):
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'user'
            }
            
            token = JWTUtils.generate_token(user_data)
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 50
    
    def test_generate_token_with_custom_expiry(self, app):
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'user'
            }
            
            token = JWTUtils.generate_token(user_data, expires_hours=1)
            
            payload = jwt.decode(
                token, 
                app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            exp_time = datetime.utcfromtimestamp(payload['exp'])
            iat_time = datetime.utcfromtimestamp(payload['iat'])
            
            time_diff = exp_time - iat_time
            assert 3300 < time_diff.total_seconds() < 3900
    
    def test_verify_token_success(self, app):
        """Test successful token ."""
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'user'
            }
            
            token = JWTUtils.generate_token(user_data)
            result = JWTUtils.verify_token(token)
            
            assert result['success'] is True
            assert result['message'] == 'Token is valid'
            assert result['data']['user_id'] == 1
            assert result['data']['email'] == 'test@example.com'
            assert result['data']['role'] == 'user'
    
    def test_verify_token_invalid(self, app):
        with app.app_context():
            result = JWTUtils.verify_token('invalid.token.here')
            
            assert result['success'] is False
            assert 'Invalid token' in result['message']
            assert result['data'] is None
    
    def test_verify_token_expired(self, app):
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'user'
            }
            
            payload = {
                'user_id': user_data['id'],
                'email': user_data['email'],
                'role': user_data['role'],
                'exp': datetime.utcnow() - timedelta(seconds=1),
                'iat': datetime.utcnow()
            }
            
            expired_token = jwt.encode(
                payload, 
                app.config['SECRET_KEY'], 
                algorithm='HS256'
            )
            
            result = JWTUtils.verify_token(expired_token)
            
            assert result['success'] is False
            assert 'expired' in result['message'].lower()
            assert result['data'] is None
    
    def test_get_user_from_token_success(self, app):
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'admin'
            }
            
            token = JWTUtils.generate_token(user_data)
            extracted_data = JWTUtils.get_user_from_token(token)
            
            assert extracted_data is not None
            assert extracted_data['user_id'] == 1
            assert extracted_data['email'] == 'test@example.com'
            assert extracted_data['role'] == 'admin'
    
    def test_get_user_from_token_invalid(self, app):
        with app.app_context():
            extracted_data = JWTUtils.get_user_from_token('invalid.token')
            assert extracted_data is None
    
    def test_refresh_token_success(self, app):
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'user'
            }
            
            original_token = JWTUtils.generate_token(user_data)
            result = JWTUtils.refresh_token(original_token)
            
            assert result['success'] is True
            assert result['message'] == 'Token refreshed successfully'
            assert result['token'] is not None
            verify_result = JWTUtils.verify_token(result['token'])
            assert verify_result['success'] is True
    
    def test_refresh_token_expired(self, app):
        with app.app_context():
            payload = {
                'user_id': 1,
                'email': 'test@example.com',
                'role': 'user',
                'exp': datetime.utcnow() - timedelta(hours=1),
                'iat': datetime.utcnow() - timedelta(hours=2)
            }
            
            expired_token = jwt.encode(
                payload, 
                app.config['SECRET_KEY'], 
                algorithm='HS256'
            )
            
            result = JWTUtils.refresh_token(expired_token)
            
            assert result['success'] is True
            assert result['token'] is not None
    
    def test_refresh_token_invalid(self, app):
        with app.app_context():
            result = JWTUtils.refresh_token('invalid.token')
            
            assert result['success'] is False
            assert 'Error refreshing token' in result['message']
            assert result['token'] is None
    
    def test_token_contains_all_required_fields(self, app):
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'user'
            }
            
            token = JWTUtils.generate_token(user_data)
            payload = jwt.decode(
                token, 
                app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            required_fields = ['user_id', 'email', 'role', 'exp', 'iat']
            for field in required_fields:
                assert field in payload
            
            assert payload['user_id'] == 1
            assert payload['email'] == 'test@example.com'
            assert payload['role'] == 'user'
    
    def test_token_expiry_time(self, app):
        with app.app_context():
            user_data = {
                'id': 1,
                'email': 'test@example.com',
                'role': 'user'
            }
            
            token = JWTUtils.generate_token(user_data, expires_hours=24)
            
            payload = jwt.decode(
                token, 
                app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            exp_time = datetime.utcfromtimestamp(payload['exp'])
            iat_time = datetime.utcfromtimestamp(payload['iat'])
            
            time_diff = exp_time - iat_time
            assert 23.5 < time_diff.total_seconds() / 3600 < 24.5
            
            now = datetime.utcnow()
            issued_diff = abs((now - iat_time).total_seconds())
            assert issued_diff < 10
    
    def test_different_users_get_different_tokens(self, app):
        with app.app_context():
            user1_data = {
                'id': 1,
                'email': 'user1@example.com',
                'role': 'user'
            }
            
            user2_data = {
                'id': 2,
                'email': 'user2@example.com',
                'role': 'admin'
            }
            
            token1 = JWTUtils.generate_token(user1_data)
            token2 = JWTUtils.generate_token(user2_data)
            
            assert token1 != token2
            
            data1 = JWTUtils.get_user_from_token(token1)
            data2 = JWTUtils.get_user_from_token(token2)
            
            assert data1['user_id'] != data2['user_id']
            assert data1['email'] != data2['email']
            assert data1['role'] != data2['role'] 