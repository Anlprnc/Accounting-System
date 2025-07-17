from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.jwt_utils import JWTUtils, token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        required_fields = ['fullname', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        result = UserService.create_user(
            fullname=data['fullname'],
            email=data['email'],
            password=data['password'],
            role='user'
        )
        
        if result['success']:
            try:
                token = JWTUtils.generate_token(result['user'])
                
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'user': result['user'],
                    'token': token,
                    'token_type': 'Bearer'
                }), 201
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'User created but token generation failed: {str(e)}'
                }), 500
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error registering user: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        result = UserService.authenticate_user(
            email=data['email'],
            password=data['password']
        )
        
        if result['success']:
            try:
                token = JWTUtils.generate_token(result['user'])
                
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'user': result['user'],
                    'token': token,
                    'token_type': 'Bearer'
                }), 200
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Authentication successful but token generation failed: {str(e)}'
                }), 500
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error logging in: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password():
    try:
        data = request.get_json()
        
        user_id = request.current_user['user_id']
        
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        result = UserService.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error changing password: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    try:
        user_id = request.current_user['user_id']
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting profile: {str(e)}'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'Authorization header is missing'
            }), 401
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({
                'success': False,
                'message': 'Invalid authorization header format'
            }), 401
        
        result = JWTUtils.refresh_token(token)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'token': result['token'],
                'token_type': 'Bearer'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error refreshing token: {str(e)}'
        }), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'Authorization header is missing'
            }), 401
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({
                'success': False,
                'message': 'Invalid authorization header format'
            }), 401
        
        result = JWTUtils.verify_token(token)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'user_data': result['data']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error verifying token: {str(e)}'
        }), 500
