from flask import Blueprint, request, jsonify
from services.invoice_service import InvoiceService
from utils.jwt_utils import token_required, admin_required

invoice_bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

@invoice_bp.route('/', methods=['GET'])
@token_required
def get_invoices():
    """Get all invoices"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = InvoiceService.get_all_invoices(page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting invoices: {str(e)}'
        }), 500

@invoice_bp.route('/<int:invoice_id>', methods=['GET'])
@token_required
def get_invoice(invoice_id):
    """Get invoice by ID"""
    try:
        invoice = InvoiceService.get_invoice_by_id(invoice_id)
        
        if not invoice:
            return jsonify({
                'success': False,
                'message': 'Invoice not found'
            }), 404
        
        return jsonify({
            'success': True,
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting invoice: {str(e)}'
        }), 500

@invoice_bp.route('/', methods=['POST'])
@token_required
def create_invoice():
    """Create new invoice"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON data'
            }), 400
        
        required_fields = ['customer_id', 'date', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Required field missing: {field}'
                }), 400
        
        result = InvoiceService.create_invoice(
            customer_id=data['customer_id'],
            date=data['date'],
            total_amount=data['total_amount'],
            status=data.get('status', 'pending')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating invoice: {str(e)}'
        }), 500

@invoice_bp.route('/<int:invoice_id>', methods=['PUT'])
@token_required
def update_invoice(invoice_id):
    """Update invoice"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON data'
            }), 400
        
        result = InvoiceService.update_invoice(invoice_id, **data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating invoice: {str(e)}'
        }), 500

@invoice_bp.route('/<int:invoice_id>', methods=['DELETE'])
@admin_required
def delete_invoice(invoice_id):
    """Delete invoice (only admin)"""
    try:
        result = InvoiceService.delete_invoice(invoice_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting invoice: {str(e)}'
        }), 500

@invoice_bp.route('/<int:invoice_id>/status', methods=['PATCH'])
@token_required
def update_invoice_status(invoice_id):
    """Update invoice status"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'message': 'Status field is required'
            }), 400
        
        result = InvoiceService.update_invoice_status(invoice_id, data['status'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating invoice status: {str(e)}'
        }), 500

@invoice_bp.route('/customer/<int:customer_id>', methods=['GET'])
@token_required
def get_invoices_by_customer(customer_id):
    """Get invoices by customer"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = InvoiceService.get_invoices_by_customer(customer_id, page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting invoices by customer: {str(e)}'
        }), 500

@invoice_bp.route('/status/<string:status>', methods=['GET'])
@token_required
def get_invoices_by_status(status):
    """Get invoices by status"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = InvoiceService.get_invoices_by_status(status, page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting invoices by status: {str(e)}'
        }), 500

@invoice_bp.route('/statistics', methods=['GET'])
@token_required
def get_invoice_statistics():
    """Get invoice statistics"""
    try:
        result = InvoiceService.get_invoice_statistics()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting invoice statistics: {str(e)}'
        }), 500

@invoice_bp.route('/pending', methods=['GET'])
@token_required
def get_pending_invoices():
    """Get pending invoices"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = InvoiceService.get_invoices_by_status('pending', page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting pending invoices: {str(e)}'
        }), 500

@invoice_bp.route('/paid', methods=['GET'])
@token_required
def get_paid_invoices():
    """Get paid invoices"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = InvoiceService.get_invoices_by_status('paid', page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting paid invoices: {str(e)}'
        }), 500

@invoice_bp.route('/overdue', methods=['GET'])
@token_required
def get_overdue_invoices():
    """Get overdue invoices"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        result = InvoiceService.get_invoices_by_status('overdue', page=page, per_page=per_page)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting overdue invoices: {str(e)}'
        }), 500
