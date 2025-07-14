import pytest
import json
from datetime import datetime


class TestAccountingRoutes:
    
    def test_get_financial_summary_success(self, client, auth_headers):
        """Test financial summary endpoint with authentication"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/summary', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'summary' in data
        assert 'total_income' in data['summary']
        assert 'total_expense' in data['summary']
        assert 'net_profit' in data['summary']
    
    def test_get_financial_summary_with_date_filters(self, client, auth_headers):
        """Test financial summary with date filters"""
        headers = auth_headers()
        
        response = client.get(
            '/api/accounting/summary?start_date=2024-01-01&end_date=2024-01-31',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['summary']['period']['start_date'] == '2024-01-01'
        assert data['summary']['period']['end_date'] == '2024-01-31'
    
    def test_get_financial_summary_invalid_date_format(self, client, auth_headers):
        """Test financial summary with invalid date format"""
        headers = auth_headers()
        
        response = client.get(
            '/api/accounting/summary?start_date=invalid-date',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'YYYY-MM-DD formatında' in data['message']
    
    def test_get_financial_summary_no_auth(self, client):
        """Test financial summary without authentication"""
        response = client.get('/api/accounting/summary')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_monthly_report_success(self, client, auth_headers):
        """Test monthly report endpoint"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/monthly-report/2024/1', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'report' in data
        assert data['report']['period']['year'] == 2024
        assert data['report']['period']['month'] == 1
        assert data['report']['period']['month_name'] == 'January'
    
    def test_get_monthly_report_invalid_month(self, client, auth_headers):
        """Test monthly report with invalid month"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/monthly-report/2024/13', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '1-12 arasında' in data['message']
    
    def test_get_monthly_report_invalid_year(self, client, auth_headers):
        """Test monthly report with invalid year"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/monthly-report/1999/1', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'arasında olmalıdır' in data['message']
    
    def test_get_cash_flow_success(self, client, auth_headers):
        """Test cash flow endpoint"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/cash-flow', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'cash_flow' in data
        assert 'daily_flow' in data['cash_flow']
        assert 'final_balance' in data['cash_flow']
    
    def test_get_cash_flow_custom_period(self, client, auth_headers):
        """Test cash flow with custom period"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/cash-flow?period_days=7', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['cash_flow']['period']['days'] == 7
        assert len(data['cash_flow']['daily_flow']) == 7
    
    def test_get_cash_flow_invalid_period(self, client, auth_headers):
        """Test cash flow with invalid period"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/cash-flow?period_days=400', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '1-365 gün arasında' in data['message']
    
    def test_get_customer_analysis_all(self, client, auth_headers):
        """Test customer analysis for all customers"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/customer-analysis', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'analysis' in data
        assert 'total_customers' in data['analysis']
        assert 'customers' in data['analysis']
    
    def test_get_customer_analysis_specific(self, client, auth_headers):
        """Test customer analysis for specific customer"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/customer-analysis/1', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'analysis' in data
        assert 'customer' in data['analysis']
        assert 'invoice_summary' in data['analysis']
    
    def test_get_customer_analysis_nonexistent(self, client, auth_headers):
        """Test customer analysis for non-existent customer"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/customer-analysis/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'bulunamadı' in data['message']
    
    def test_get_customer_analysis_with_query_param(self, client, auth_headers):
        """Test customer analysis with query parameter"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/customer-analysis?customer_id=1', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'analysis' in data
    
    def test_get_invoice_summary_success(self, client, auth_headers):
        """Test invoice status summary endpoint"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/invoice-summary', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'invoice_summary' in data
        assert 'by_status' in data['invoice_summary']
        assert 'totals' in data['invoice_summary']
    
    def test_get_profit_loss_statement_success(self, client, auth_headers):
        """Test profit and loss statement endpoint"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/profit-loss', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'profit_loss' in data
        assert 'revenue' in data['profit_loss']
        assert 'expenses' in data['profit_loss']
        assert 'profit' in data['profit_loss']
    
    def test_get_profit_loss_statement_with_dates(self, client, auth_headers):
        """Test profit and loss statement with date filters"""
        headers = auth_headers()
        
        response = client.get(
            '/api/accounting/profit-loss?start_date=2024-01-01&end_date=2024-01-31',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['profit_loss']['period']['start_date'] == '2024-01-01'
        assert data['profit_loss']['period']['end_date'] == '2024-01-31'
    
    def test_get_profit_loss_statement_invalid_date(self, client, auth_headers):
        """Test profit and loss statement with invalid date"""
        headers = auth_headers()
        
        response = client.get(
            '/api/accounting/profit-loss?start_date=invalid',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'YYYY-MM-DD formatında' in data['message']
    
    def test_get_transaction_summary_success(self, client, auth_headers):
        """Test transaction summary by type endpoint"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/transaction-summary', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'transaction_summary' in data
    
    def test_get_dashboard_data_success(self, client, auth_headers):
        """Test dashboard data endpoint"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'dashboard' in data
        assert 'financial_summary' in data['dashboard']
        assert 'invoice_summary' in data['dashboard']
        assert 'transaction_summary' in data['dashboard']
        assert 'cash_flow_summary' in data['dashboard']
        assert 'last_updated' in data['dashboard']
    
    def test_get_yearly_report_success(self, client, auth_headers):
        """Test yearly report endpoint"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/reports/yearly/2024', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'yearly_report' in data
        assert data['yearly_report']['year'] == 2024
        assert 'financial_summary' in data['yearly_report']
        assert 'profit_loss' in data['yearly_report']
        assert 'monthly_breakdown' in data['yearly_report']
        assert len(data['yearly_report']['monthly_breakdown']) == 12
    
    def test_get_yearly_report_invalid_year(self, client, auth_headers):
        """Test yearly report with invalid year"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/reports/yearly/1999', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'arasında olmalıdır' in data['message']
    
    def test_health_check_success(self, client):
        """Test health check endpoint (no auth required)"""
        response = client.get('/api/accounting/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'çalışıyor' in data['message']
        assert 'timestamp' in data
    
    def test_all_endpoints_require_auth_except_health(self, client):
        """Test that all endpoints except health require authentication"""
        endpoints = [
            '/api/accounting/summary',
            '/api/accounting/monthly-report/2024/1',
            '/api/accounting/cash-flow',
            '/api/accounting/customer-analysis',
            '/api/accounting/customer-analysis/1',
            '/api/accounting/invoice-summary',
            '/api/accounting/profit-loss',
            '/api/accounting/transaction-summary',
            '/api/accounting/dashboard',
            '/api/accounting/reports/yearly/2024'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require auth"
            data = response.get_json()
            assert data['success'] is False
    
    def test_admin_user_can_access_all_endpoints(self, client, admin_headers):
        """Test that admin users can access all accounting endpoints"""
        headers = admin_headers()
        
        endpoints = [
            '/api/accounting/summary',
            '/api/accounting/monthly-report/2024/1',
            '/api/accounting/cash-flow',
            '/api/accounting/customer-analysis',
            '/api/accounting/customer-analysis/1',
            '/api/accounting/invoice-summary',
            '/api/accounting/profit-loss',
            '/api/accounting/transaction-summary',
            '/api/accounting/dashboard',
            '/api/accounting/reports/yearly/2024'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code in [200, 404], f"Admin should access {endpoint}"
            # 404 is acceptable for endpoints like customer-analysis/1 if customer doesn't exist
    
    def test_error_handling_for_service_failures(self, client, auth_headers):
        """Test error handling when service methods fail"""
        headers = auth_headers()
        
        # Test with extreme date range that might cause issues
        response = client.get(
            '/api/accounting/cash-flow?period_days=0',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_json_response_format(self, client, auth_headers):
        """Test that all responses follow consistent JSON format"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/summary', headers=headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'success' in data
        assert isinstance(data['success'], bool)
    
    def test_monthly_report_boundary_values(self, client, auth_headers):
        """Test monthly report with boundary values"""
        headers = auth_headers()
        
        # Test month 0
        response = client.get('/api/accounting/monthly-report/2024/0', headers=headers)
        assert response.status_code == 400
        
        # Test month 1 (valid)
        response = client.get('/api/accounting/monthly-report/2024/1', headers=headers)
        assert response.status_code == 200
        
        # Test month 12 (valid)
        response = client.get('/api/accounting/monthly-report/2024/12', headers=headers)
        assert response.status_code == 200
        
        # Test month 13
        response = client.get('/api/accounting/monthly-report/2024/13', headers=headers)
        assert response.status_code == 400
    
    def test_cash_flow_boundary_values(self, client, auth_headers):
        """Test cash flow with boundary values"""
        headers = auth_headers()
        
        # Test 0 days
        response = client.get('/api/accounting/cash-flow?period_days=0', headers=headers)
        assert response.status_code == 400
        
        # Test 1 day (valid)
        response = client.get('/api/accounting/cash-flow?period_days=1', headers=headers)
        assert response.status_code == 200
        
        # Test 365 days (valid)
        response = client.get('/api/accounting/cash-flow?period_days=365', headers=headers)
        assert response.status_code == 200
        
        # Test 366 days
        response = client.get('/api/accounting/cash-flow?period_days=366', headers=headers)
        assert response.status_code == 400
    
    def test_dashboard_data_completeness(self, client, auth_headers):
        """Test that dashboard contains all required data"""
        headers = auth_headers()
        
        response = client.get('/api/accounting/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        dashboard = data['dashboard']
        
        # Check all required sections exist
        required_sections = [
            'financial_summary',
            'invoice_summary', 
            'transaction_summary',
            'cash_flow_summary',
            'last_updated'
        ]
        
        for section in required_sections:
            assert section in dashboard, f"Dashboard missing {section}"
        
        # Verify cash_flow_summary structure
        assert 'final_balance' in dashboard['cash_flow_summary']
        assert 'period_days' in dashboard['cash_flow_summary']
        assert dashboard['cash_flow_summary']['period_days'] == 30 