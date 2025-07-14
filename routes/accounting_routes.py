from flask import Blueprint, request, jsonify
from services.accounting_service import AccountingService
from utils.jwt_utils import token_required, admin_required
from datetime import datetime

accounting_bp = Blueprint('accounting', __name__, url_prefix='/api/accounting')

@accounting_bp.route('/summary', methods=['GET'])
@token_required
def get_financial_summary():
    """
    Finansal özet raporu endpoint'i
    Query parametreleri: start_date, end_date (YYYY-MM-DD formatında)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Tarih validasyonu
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Başlangıç tarihi YYYY-MM-DD formatında olmalıdır'
                }), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Bitiş tarihi YYYY-MM-DD formatında olmalıdır'
                }), 400
        
        result = AccountingService.get_financial_summary(start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Finansal özet alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/monthly-report/<int:year>/<int:month>', methods=['GET'])
@token_required
def get_monthly_report(year, month):
    """
    Aylık muhasebe raporu endpoint'i
    """
    try:
        # Ay validasyonu
        if month < 1 or month > 12:
            return jsonify({
                'success': False,
                'message': 'Ay 1-12 arasında olmalıdır'
            }), 400
        
        # Yıl validasyonu
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 10:
            return jsonify({
                'success': False,
                'message': f'Yıl 2000-{current_year + 10} arasında olmalıdır'
            }), 400
        
        result = AccountingService.get_monthly_report(year, month)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Aylık rapor alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/cash-flow', methods=['GET'])
@token_required
def get_cash_flow():
    """
    Nakit akışı raporu endpoint'i
    Query parametresi: period_days (varsayılan: 30)
    """
    try:
        period_days = request.args.get('period_days', 30, type=int)
        
        # Periyot validasyonu
        if period_days < 1 or period_days > 365:
            return jsonify({
                'success': False,
                'message': 'Periyot 1-365 gün arasında olmalıdır'
            }), 400
        
        result = AccountingService.get_cash_flow(period_days)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Nakit akışı raporu alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/customer-analysis', methods=['GET'])
@token_required
def get_customer_analysis():
    """
    Müşteri finansal analizi endpoint'i
    Query parametresi: customer_id (isteğe bağlı)
    """
    try:
        customer_id = request.args.get('customer_id', type=int)
        
        result = AccountingService.get_customer_analysis(customer_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'bulunamadı' in result.get('message', '') else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Müşteri analizi alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/customer-analysis/<int:customer_id>', methods=['GET'])
@token_required
def get_specific_customer_analysis(customer_id):
    """
    Belirli müşteri finansal analizi endpoint'i
    """
    try:
        result = AccountingService.get_customer_analysis(customer_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404 if 'bulunamadı' in result.get('message', '') else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Müşteri analizi alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/invoice-summary', methods=['GET'])
@token_required
def get_invoice_status_summary():
    """
    Fatura durum özeti endpoint'i
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
            'message': f'Fatura özeti alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/profit-loss', methods=['GET'])
@token_required
def get_profit_loss_statement():
    """
    Kar-zarar tablosu endpoint'i
    Query parametreleri: start_date, end_date (YYYY-MM-DD formatında)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Tarih validasyonu
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Başlangıç tarihi YYYY-MM-DD formatında olmalıdır'
                }), 400
        
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Bitiş tarihi YYYY-MM-DD formatında olmalıdır'
                }), 400
        
        result = AccountingService.get_profit_loss_statement(start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Kar-zarar tablosu alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/transaction-summary', methods=['GET'])
@token_required
def get_transaction_summary_by_type():
    """
    İşlem tipine göre özet endpoint'i
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
            'message': f'İşlem özeti alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_data():
    """
    Muhasebe dashboard'u için tüm temel verileri getiren endpoint
    """
    try:
        # Finansal özet (son 30 gün)
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
            'message': f'Dashboard verileri alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/reports/yearly/<int:year>', methods=['GET'])
@token_required
def get_yearly_report(year):
    """
    Yıllık muhasebe raporu endpoint'i
    """
    try:
        # Yıl validasyonu
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 10:
            return jsonify({
                'success': False,
                'message': f'Yıl 2000-{current_year + 10} arasında olmalıdır'
            }), 400
        
        # Yıl başı ve sonu tarihleri
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        # Yıllık veriler
        financial_summary = AccountingService.get_financial_summary(start_date, end_date)
        profit_loss = AccountingService.get_profit_loss_statement(start_date, end_date)
        
        # Aylık breakdown
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
            'message': f'Yıllık rapor alınırken hata: {str(e)}'
        }), 500

@accounting_bp.route('/health', methods=['GET'])
def health_check():
    """
    Muhasebe servisi sağlık kontrolü
    """
    return jsonify({
        'success': True,
        'message': 'Muhasebe servisi çalışıyor',
        'timestamp': datetime.now().isoformat()
    }), 200
