from flask import Blueprint, request, jsonify
from services.transaction_service import TransactionService
from utils.jwt_utils import token_required, admin_required

transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@transaction_bp.route('/', methods=['GET'])
@token_required
def get_transactions():
    """Get all transactions"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = TransactionService.get_all_transactions(page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting transactions: {str(e)}'
        }), 500

@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
@token_required
def get_transaction(transaction_id):
    """Get transaction by ID"""
    try:
        transaction = TransactionService.get_transaction_by_id(transaction_id)
        
        if not transaction:
            return jsonify({
                'success': False,
                'message': 'Transaction not found'
            }), 404
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting transaction: {str(e)}'
        }), 500

@transaction_bp.route('/', methods=['POST'])
@token_required
def create_transaction():
    """Create new transaction"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Transaction information is missing'
            }), 400
        
        required_fields = ['invoice_id', 'amount', 'date', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Required field is missing: {field}'
                }), 400
        
        result = TransactionService.create_transaction(
            invoice_id=data['invoice_id'],
            amount=data['amount'],
            date=data['date'],
            type=data['type']
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating transaction: {str(e)}'
        }), 500

@transaction_bp.route('/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction(transaction_id):
    """Update transaction"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Update data is missing'
            }), 400
        
        data.pop('id', None)
        
        result = TransactionService.update_transaction(transaction_id, **data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result['message'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating transaction: {str(e)}'
        }), 500

@transaction_bp.route('/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction(transaction_id):
    """Delete transaction"""
    try:
        result = TransactionService.delete_transaction(transaction_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result['message'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting transaction: {str(e)}'
        }), 500

@transaction_bp.route('/by-invoice/<int:invoice_id>', methods=['GET'])
@token_required
def get_transactions_by_invoice(invoice_id):
    """Get transactions by invoice"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = TransactionService.get_transactions_by_invoice(
            invoice_id=invoice_id,
            page=page,
            per_page=per_page
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result['message'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting transactions by invoice: {str(e)}'
        }), 500

@transaction_bp.route('/by-type/<string:type>', methods=['GET'])
@token_required
def get_transactions_by_type(type):
    """Get transactions by type"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = TransactionService.get_transactions_by_type(
            type=type,
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
            'message': f'Error getting transactions by type: {str(e)}'
        }), 500

@transaction_bp.route('/search', methods=['GET'])
@token_required
def search_transactions():
    """Search transactions"""
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
        
        result = TransactionService.search_transactions(
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
            'message': f'Error searching transactions: {str(e)}'
        }), 500

@transaction_bp.route('/stats', methods=['GET'])
@token_required
def get_transaction_statistics():
    """Get transaction statistics"""
    try:
        result = TransactionService.get_transaction_statistics()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting statistics: {str(e)}'
        }), 500
