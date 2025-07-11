from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.jwt_utils import token_required, admin_required

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
@admin_required
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = UserService.get_all_users(page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting users: {str(e)}'
        }), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    try:
        current_user_id = request.current_user['user_id']
        current_user_role = request.current_user['role']
        
        if current_user_id != user_id and current_user_role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Access denied: You can only view your own profile'
            }), 403
        
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
            'message': f'Error getting user: {str(e)}'
        }), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    try:
        current_user_id = request.current_user['user_id']
        current_user_role = request.current_user['role']
        
        if current_user_id != user_id and current_user_role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Access denied: You can only update your own profile'
            }), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Data to update is not provided'
            }), 400
        
        data.pop('id', None)
        if current_user_role != 'admin' and 'role' in data:
            data.pop('role')
        
        result = UserService.update_user(user_id, **data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating user: {str(e)}'
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        result = UserService.delete_user(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result['message'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting user: {str(e)}'
        }), 500

@user_bp.route('/search', methods=['GET'])
@admin_required
def search_users():
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400
        
        per_page = min(per_page, 100)
        
        result = UserService.search_users(
            query=query,
            page=page,
            per_page=per_page
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching users: {str(e)}'
        }), 500

@user_bp.route('/by-role/<string:role>', methods=['GET'])
@admin_required
def get_users_by_role(role):
    try:
        users = UserService.get_users_by_role(role)
        
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users],
            'count': len(users),
            'role': role
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting users by role: {str(e)}'
        }), 500

@user_bp.route('/by-email/<string:email>', methods=['GET'])
@admin_required
def get_user_by_email(email):
    try:
        user = UserService.get_user_by_email(email)
        
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
            'message': f'Error getting user by email: {str(e)}'
        }), 500

@user_bp.route('/stats', methods=['GET'])
@admin_required
def get_user_stats():
    try:
        all_users_result = UserService.get_all_users(page=1, per_page=1)
        total_users = all_users_result.get('total', 0)
        
        admin_users = len(UserService.get_users_by_role('admin'))
        regular_users = len(UserService.get_users_by_role('user'))
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'admin_users': admin_users,
                'regular_users': regular_users,
                'roles': {
                    'admin': admin_users,
                    'user': regular_users
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting user stats: {str(e)}'
        }), 500

@user_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
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
            'message': f'Error getting current user: {str(e)}'
        }), 500

@user_bp.route('/me', methods=['PUT'])
@token_required
def update_current_user():
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Data to update is not provided'
            }), 400
        
        data.pop('id', None)
        data.pop('role', None)
        
        result = UserService.update_user(user_id, **data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating current user: {str(e)}'
        }), 500
