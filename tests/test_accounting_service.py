import pytest
from services.accounting_service import AccountingService
from models.transaction import Transaction
from models.invoice import Invoice
from models.customer import Customer
from models.user import db
from datetime import datetime, date


class TestAccountingService:
    
    def test_get_financial_summary_success(self, app):
        """Test financial summary calculation"""
        with app.app_context():
            result = AccountingService.get_financial_summary()
            
            assert result['success'] is True
            assert 'summary' in result
            assert 'total_income' in result['summary']
            assert 'total_expense' in result['summary']
            assert 'net_profit' in result['summary']
            assert result['summary']['total_income'] == 2500.0  # 1000 + 1500
            assert result['summary']['total_expense'] == 800.0   # 500 + 300
            assert result['summary']['net_profit'] == 1700.0     # 2500 - 800
    
    def test_get_financial_summary_with_date_filter(self, app):
        """Test financial summary with date filters"""
        with app.app_context():
            # Test January 2024 only
            result = AccountingService.get_financial_summary(
                start_date='2024-01-01',
                end_date='2024-01-31'
            )
            
            assert result['success'] is True
            # January has 1000 income and 800 expense (500 + 300)
            assert result['summary']['total_income'] == 1000.0
            assert result['summary']['total_expense'] == 800.0
            assert result['summary']['net_profit'] == 200.0
    
    def test_get_monthly_report_success(self, app):
        """Test monthly report generation"""
        with app.app_context():
            result = AccountingService.get_monthly_report(2024, 1)
            
            assert result['success'] is True
            assert 'report' in result
            assert result['report']['period']['year'] == 2024
            assert result['report']['period']['month'] == 1
            assert result['report']['period']['month_name'] == 'January'
            assert result['report']['summary']['total_income'] == 1000.0
            assert result['report']['summary']['total_expense'] == 800.0
            assert result['report']['summary']['net_profit'] == 200.0
    
    def test_get_monthly_report_february(self, app):
        """Test monthly report for February"""
        with app.app_context():
            result = AccountingService.get_monthly_report(2024, 2)
            
            assert result['success'] is True
            # February has only 1500 income, no expenses
            assert result['report']['summary']['total_income'] == 1500.0
            assert result['report']['summary']['total_expense'] == 0.0
            assert result['report']['summary']['net_profit'] == 1500.0
    
    def test_get_cash_flow_success(self, app):
        """Test cash flow calculation"""
        with app.app_context():
            result = AccountingService.get_cash_flow(period_days=60)
            
            assert result['success'] is True
            assert 'cash_flow' in result
            assert 'daily_flow' in result['cash_flow']
            assert 'final_balance' in result['cash_flow']
            # Test data is from 2024, so cash flow might be 0 for current period
            assert isinstance(result['cash_flow']['final_balance'], float)
    
    def test_get_customer_analysis_all_customers(self, app):
        """Test customer analysis for all customers"""
        with app.app_context():
            result = AccountingService.get_customer_analysis()
            
            assert result['success'] is True
            assert 'analysis' in result
            assert result['analysis']['total_customers'] == 2
            assert len(result['analysis']['customers']) == 2
            
            # Find customer 1 analysis
            customer1_analysis = next(
                (c for c in result['analysis']['customers'] 
                 if c['customer']['name'] == 'Test Müşteri 1'), 
                None
            )
            assert customer1_analysis is not None
            assert customer1_analysis['invoice_count'] == 2  # 2 invoices
            assert customer1_analysis['total_amount'] == 2500.0  # 1000 + 1500
    
    def test_get_customer_analysis_specific_customer(self, app):
        """Test customer analysis for specific customer"""
        with app.app_context():
            result = AccountingService.get_customer_analysis(customer_id=1)
            
            assert result['success'] is True
            assert 'analysis' in result
            assert result['analysis']['customer']['name'] == 'Test Müşteri 1'
            assert result['analysis']['invoice_summary']['total_invoices'] == 2
            assert result['analysis']['invoice_summary']['total_amount'] == 2500.0
            assert result['analysis']['invoice_summary']['paid_invoices'] == 2
            assert result['analysis']['invoice_summary']['pending_invoices'] == 0
    
    def test_get_customer_analysis_nonexistent_customer(self, app):
        """Test customer analysis for non-existent customer"""
        with app.app_context():
            result = AccountingService.get_customer_analysis(customer_id=999)
            
            assert result['success'] is False
            assert 'Müşteri bulunamadı' in result['message']
    
    def test_get_invoice_status_summary_success(self, app):
        """Test invoice status summary"""
        with app.app_context():
            result = AccountingService.get_invoice_status_summary()
            
            assert result['success'] is True
            assert 'invoice_summary' in result
            assert 'by_status' in result['invoice_summary']
            assert 'totals' in result['invoice_summary']
            
            # Check status breakdown
            by_status = result['invoice_summary']['by_status']
            assert 'paid' in by_status
            assert 'pending' in by_status
            assert by_status['paid']['count'] == 2  # 2 paid invoices
            assert by_status['paid']['total_amount'] == 2500.0  # 1000 + 1500
            assert by_status['pending']['count'] == 1  # 1 pending invoice
            assert by_status['pending']['total_amount'] == 2000.0
    
    def test_get_profit_loss_statement_success(self, app):
        """Test profit and loss statement"""
        with app.app_context():
            result = AccountingService.get_profit_loss_statement(
                start_date='2024-01-01',
                end_date='2024-02-28'
            )
            
            assert result['success'] is True
            assert 'profit_loss' in result
            assert result['profit_loss']['revenue']['total_revenue'] == 2500.0  # paid invoices
            assert result['profit_loss']['expenses']['total_expenses'] == 800.0  # expense transactions
            assert result['profit_loss']['profit']['gross_profit'] == 1700.0
            assert result['profit_loss']['profit']['net_profit'] == 1700.0
    
    def test_get_profit_loss_statement_with_defaults(self, app):
        """Test profit and loss statement with default dates"""
        with app.app_context():
            result = AccountingService.get_profit_loss_statement()
            
            assert result['success'] is True
            assert 'profit_loss' in result
            # Should use current month as default
    
    def test_get_transaction_summary_by_type_success(self, app):
        """Test transaction summary by type"""
        with app.app_context():
            result = AccountingService.get_transaction_summary_by_type()
            
            assert result['success'] is True
            assert 'transaction_summary' in result
            
            summary = result['transaction_summary']
            assert 'income' in summary
            assert 'expense' in summary
            
            # Income summary
            assert summary['income']['count'] == 2  # 2 income transactions
            assert summary['income']['total_amount'] == 2500.0  # 1000 + 1500
            assert summary['income']['average_amount'] == 1250.0  # 2500 / 2
            
            # Expense summary
            assert summary['expense']['count'] == 2  # 2 expense transactions
            assert summary['expense']['total_amount'] == 800.0  # 500 + 300
            assert summary['expense']['average_amount'] == 400.0  # 800 / 2
    
    def test_get_financial_summary_empty_result(self, app):
        """Test financial summary with no matching data"""
        with app.app_context():
            # Test with future dates where no data exists
            result = AccountingService.get_financial_summary(
                start_date='2025-01-01',
                end_date='2025-01-31'
            )
            
            assert result['success'] is True
            assert result['summary']['total_income'] == 0.0
            assert result['summary']['total_expense'] == 0.0
            assert result['summary']['net_profit'] == 0.0
    
    def test_get_monthly_report_no_data(self, app):
        """Test monthly report with no data"""
        with app.app_context():
            result = AccountingService.get_monthly_report(2025, 1)
            
            assert result['success'] is True
            assert result['report']['summary']['total_income'] == 0.0
            assert result['report']['summary']['total_expense'] == 0.0
            assert result['report']['summary']['net_profit'] == 0.0
            assert result['report']['summary']['transaction_count'] == 0
    
    def test_invalid_date_handling(self, app):
        """Test handling of invalid dates"""
        with app.app_context():
            # This should not raise an exception but handle gracefully
            try:
                result = AccountingService.get_financial_summary(
                    start_date='invalid-date',
                    end_date='2024-01-31'
                )
                # Should fail gracefully
                assert result['success'] is False
            except ValueError:
                # It's acceptable to raise ValueError for invalid dates
                pass
    
    def test_get_cash_flow_edge_cases(self, app):
        """Test cash flow with edge cases"""
        with app.app_context():
            # Test with 1 day period
            result = AccountingService.get_cash_flow(period_days=1)
            
            assert result['success'] is True
            assert result['cash_flow']['period']['days'] == 1
            assert len(result['cash_flow']['daily_flow']) == 1
    
    def test_profit_margin_calculation(self, app):
        """Test profit margin calculation in profit/loss statement"""
        with app.app_context():
            result = AccountingService.get_profit_loss_statement(
                start_date='2024-01-01',
                end_date='2024-02-28'
            )
            
            assert result['success'] is True
            profit_data = result['profit_loss']['profit']
            
            # Profit margin = (net_profit / total_revenue) * 100
            expected_margin = (1700.0 / 2500.0) * 100  # 68%
            assert abs(profit_data['profit_margin'] - expected_margin) < 0.01
    
    def test_zero_revenue_profit_margin(self, app):
        """Test profit margin calculation with zero revenue"""
        with app.app_context():
            # Test with dates that have no paid invoices
            result = AccountingService.get_profit_loss_statement(
                start_date='2025-01-01',
                end_date='2025-01-31'
            )
            
            assert result['success'] is True
            # Should handle division by zero gracefully
            assert result['profit_loss']['profit']['profit_margin'] == 0.0 