import jwt
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps
from typing import Dict, Any, Optional


class JWTUtils:
    @staticmethod
    def generate_token(user_data: Dict[str, Any], expires_hours: int = 24) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_data: User information to include in token
            expires_hours: Token expiration time in hours
            
        Returns:
            str: JWT token
        """
        try:
            payload = {
                'user_id': user_data['id'],
                'email': user_data['email'],
                'role': user_data['role'],
                'exp': datetime.utcnow() + timedelta(hours=expires_hours),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(
                payload, 
                current_app.config['SECRET_KEY'], 
                algorithm='HS256'
            )
            
            return token
            
        except Exception as e:
            raise Exception(f"Error generating token: {str(e)}")
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Dict: Decoded token data or error
        """
        try:
            payload = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            return {
                'success': True,
                'data': payload,
                'message': 'Token is valid'
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'data': None,
                'message': 'Token has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'data': None,
                'message': 'Invalid token'
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'Error verifying token: {str(e)}'
            }
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user data from token
        
        Args:
            token: JWT token string
            
        Returns:
            Dict: User data or None
        """
        result = JWTUtils.verify_token(token)
        
        if result['success']:
            return result['data']
        return None
    
    @staticmethod
    def refresh_token(token: str, expires_hours: int = 24) -> Dict[str, Any]:
        """
        Refresh an existing token
        
        Args:
            token: Current JWT token
            expires_hours: New token expiration time
            
        Returns:
            Dict: New token or error
        """
        try:
            payload = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=['HS256'],
                options={"verify_exp": False}
            )
            
            user_data = {
                'id': payload['user_id'],
                'email': payload['email'],
                'role': payload['role']
            }
            
            new_token = JWTUtils.generate_token(user_data, expires_hours)
            
            return {
                'success': True,
                'token': new_token,
                'message': 'Token refreshed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'token': None,
                'message': f'Error refreshing token: {str(e)}'
            }


def token_required(f):
    """
    Decorator to require valid JWT token for routes
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, jsonify
        
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid authorization header format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401
        
        result = JWTUtils.verify_token(token)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
        
        request.current_user = result['data']
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to require admin role
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        from flask import request, jsonify
        
        if request.current_user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated 