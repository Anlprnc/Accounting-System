from flask import Blueprint, request, jsonify
from services.accounting_service import AccountingService
from utils.jwt_utils import token_required, admin_required
from datetime import datetime

accounting_bp = Blueprint('accounting', __name__, url_prefix='/api/accounting')

@accounting_bp.route('/summary', methods=['GET'])
@token_required
def get_financial_summary():
    """
    Financial summary report endpoint
    Query parameters: start_date, end_date (YYYY-MM-DD format)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Start date must be in YYYY-MM-DD format'
                }), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'End date must be in YYYY-MM-DD format'
                }), 400
        
        result = AccountingService.get_financial_summary(start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting financial summary: {str(e)}'
        }), 500

@accounting_bp.route('/monthly-report/<int:year>/<int:month>', methods=['GET'])
@token_required
def get_monthly_report(year, month):
    """
    Monthly accounting report endpoint
    """
    try:
        if month < 1 or month > 12:
            return jsonify({
                'success': False,
                'message': 'Month must be between 1 and 12'
            }), 400
        
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 10:
            return jsonify({
                'success': False,
                'message': f'Year must be between 2000 and {current_year + 10}'
            }), 400
        
        result = AccountingService.get_monthly_report(year, month)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting monthly report: {str(e)}'
        }), 500

@accounting_bp.route('/cash-flow', methods=['GET'])
@token_required
def get_cash_flow():
    """
    Cash
    """
    try:
        period_days = request.args.get('period_days', 30, type=int)
        
        if period_days < 1 or period_days > 365:
            return jsonify({
                'success': False,
                'message': 'Period must be between 1 and 365 days'
            }), 400
        
        result = AccountingService.get_cash_flow(period_days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting cash flow: {str(e)}'
        }), 500

@accounting_bp.route('/customer-analysis', methods=['GET'])
@token_required
def get_customer_analysis():
    """
    Customer financial analysis endpoint
    Query parameter: customer_id (optional)
    """
    try:
        customer_id = request.args.get('customer_id', type=int)
        
        result = AccountingService.get_customer_analysis(customer_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result.get('message', '') else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting customer analysis: {str(e)}'
        }), 500

@accounting_bp.route('/customer-analysis/<int:customer_id>', methods=['GET'])
@token_required
def get_specific_customer_analysis(customer_id):
    """
    Specific customer financial analysis endpoint
    """
    try:
        result = AccountingService.get_customer_analysis(customer_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'not found' in result.get('message', '') else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting customer analysis: {str(e)}'
        }), 500

@accounting_bp.route('/invoice-summary', methods=['GET'])
@token_required
def get_invoice_status_summary():
    """
    Invoice status summary endpoint
    """
    try:
        result = AccountingService.get_invoice_status_summary()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting invoice status summary: {str(e)}'
        }), 500

@accounting_bp.route('/profit-loss', methods=['GET'])
@token_required
def get_profit_loss_statement():
    """
    Profit and loss statement endpoint
    Query parameters: start_date, end_date (YYYY-MM-DD format)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Start date must be in YYYY-MM-DD format'
                }), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'End date must be in YYYY-MM-DD format'
                }), 400
        
        result = AccountingService.get_profit_loss_statement(start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting profit and loss statement: {str(e)}'
        }), 500

@accounting_bp.route('/transaction-summary', methods=['GET'])
@token_required
def get_transaction_summary_by_type():
    """
    Transaction type summary endpoint
    """
    try:
        result = AccountingService.get_transaction_summary_by_type()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting transaction summary: {str(e)}'
        }), 500

@accounting_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_data():
    """
    Accounting dashboard endpoint
    """
    try:
        end_date = datetime.now().date().isoformat()
        start_date = (datetime.now().date().replace(day=1)).isoformat()
        
        financial_summary = AccountingService.get_financial_summary(start_date, end_date)
        invoice_summary = AccountingService.get_invoice_status_summary()
        transaction_summary = AccountingService.get_transaction_summary_by_type()
        cash_flow = AccountingService.get_cash_flow(30)
        
        dashboard_data = {
            'success': True,
            'dashboard': {
                'financial_summary': financial_summary.get('summary'),
                'invoice_summary': invoice_summary.get('invoice_summary'),
                'transaction_summary': transaction_summary.get('transaction_summary'),
                'cash_flow_summary': {
                    'final_balance': cash_flow.get('cash_flow', {}).get('final_balance', 0),
                    'period_days': 30
                },
                'last_updated': datetime.now().isoformat()
            }
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting dashboard data: {str(e)}'
        }), 500

@accounting_bp.route('/reports/yearly/<int:year>', methods=['GET'])
@token_required
def get_yearly_report(year):
    """
    Yearly accounting report endpoint
    """
    try:
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 10:
            return jsonify({
                'success': False,
                'message': f'Year must be between 2000 and {current_year + 10}'
            }), 400
        
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        financial_summary = AccountingService.get_financial_summary(start_date, end_date)
        profit_loss = AccountingService.get_profit_loss_statement(start_date, end_date)
        
        monthly_data = []
        for month in range(1, 13):
            monthly_report = AccountingService.get_monthly_report(year, month)
            if monthly_report['success']:
                monthly_data.append({
                    'month': month,
                    'month_name': monthly_report['report']['period']['month_name'],
                    'summary': monthly_report['report']['summary']
                })
        
        yearly_report = {
            'success': True,
            'yearly_report': {
                'year': year,
                'financial_summary': financial_summary.get('summary'),
                'profit_loss': profit_loss.get('profit_loss'),
                'monthly_breakdown': monthly_data
            }
        }
        
        return jsonify(yearly_report), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting yearly report: {str(e)}'
        }), 500

@accounting_bp.route('/health', methods=['GET'])
def health_check():
    """
    Accounting service health check
    """
    return jsonify({
        'success': True,
        'message': 'Accounting service is running',
        'timestamp': datetime.now().isoformat()
    }), 200
