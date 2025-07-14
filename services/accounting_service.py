from models.transaction import Transaction, db
from models.invoice import Invoice
from models.customer import Customer
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import calendar


class AccountingService:
    
    @staticmethod
    def get_financial_summary(start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Finansal özet raporu
        
        Args:
            start_date: Başlangıç tarihi (YYYY-MM-DD)
            end_date: Bitiş tarihi (YYYY-MM-DD)
            
        Returns:
            Dict: Finansal özet bilgileri
        """
        try:
            query = db.session.query(Transaction)
            
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date >= start_date_obj)
            
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Transaction.date <= end_date_obj)
            
            # Gelir (income) ve gider (expense) hesaplaması
            income_total = query.filter(Transaction.type == 'income').with_entities(
                func.sum(Transaction.amount).label('total')
            ).scalar() or 0.0
            
            expense_total = query.filter(Transaction.type == 'expense').with_entities(
                func.sum(Transaction.amount).label('total')
            ).scalar() or 0.0
            
            # Net kar/zarar
            net_profit = income_total - expense_total
            
            # İşlem sayıları
            income_count = query.filter(Transaction.type == 'income').count()
            expense_count = query.filter(Transaction.type == 'expense').count()
            
            return {
                'success': True,
                'summary': {
                    'total_income': float(income_total),
                    'total_expense': float(expense_total),
                    'net_profit': float(net_profit),
                    'income_transactions': income_count,
                    'expense_transactions': expense_count,
                    'period': {
                        'start_date': start_date,
                        'end_date': end_date
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Finansal özet hesaplanırken hata: {str(e)}',
                'summary': None
            }
    
    @staticmethod
    def get_monthly_report(year: int, month: int) -> Dict[str, Any]:
        """
        Aylık muhasebe raporu
        
        Args:
            year: Yıl
            month: Ay (1-12)
            
        Returns:
            Dict: Aylık rapor bilgileri
        """
        try:
            # Ayın ilk ve son günü
            first_day = datetime(year, month, 1).date()
            last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
            
            # Aylık işlemler
            monthly_transactions = db.session.query(Transaction).filter(
                and_(
                    Transaction.date >= first_day,
                    Transaction.date <= last_day
                )
            ).all()
            
            # Gelir ve gider ayrımı
            income_transactions = [t for t in monthly_transactions if t.type == 'income']
            expense_transactions = [t for t in monthly_transactions if t.type == 'expense']
            
            monthly_income = sum(t.amount for t in income_transactions)
            monthly_expense = sum(t.amount for t in expense_transactions)
            
            # Günlük detaylar
            daily_summary = {}
            for transaction in monthly_transactions:
                day_key = transaction.date.strftime('%Y-%m-%d')
                if day_key not in daily_summary:
                    daily_summary[day_key] = {'income': 0.0, 'expense': 0.0}
                
                if transaction.type == 'income':
                    daily_summary[day_key]['income'] += transaction.amount
                else:
                    daily_summary[day_key]['expense'] += transaction.amount
            
            return {
                'success': True,
                'report': {
                    'period': {
                        'year': year,
                        'month': month,
                        'month_name': calendar.month_name[month],
                        'start_date': first_day.isoformat(),
                        'end_date': last_day.isoformat()
                    },
                    'summary': {
                        'total_income': float(monthly_income),
                        'total_expense': float(monthly_expense),
                        'net_profit': float(monthly_income - monthly_expense),
                        'transaction_count': len(monthly_transactions)
                    },
                    'daily_breakdown': daily_summary,
                    'transactions': [t.to_dict() for t in monthly_transactions]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Aylık rapor oluşturulurken hata: {str(e)}',
                'report': None
            }
    
    @staticmethod
    def get_cash_flow(period_days: int = 30) -> Dict[str, Any]:
        """
        Nakit akışı raporu
        
        Args:
            period_days: Rapor periyodu (gün)
            
        Returns:
            Dict: Nakit akışı bilgileri
        """
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=period_days - 1)
            
            # Periyot içindeki işlemler
            transactions = db.session.query(Transaction).filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            ).order_by(Transaction.date.asc()).all()
            
            # Günlük nakit akışı hesaplama
            cash_flow = []
            running_balance = 0.0
            
            current_date = start_date
            while current_date <= end_date:
                daily_transactions = [t for t in transactions if t.date == current_date]
                daily_income = sum(t.amount for t in daily_transactions if t.type == 'income')
                daily_expense = sum(t.amount for t in daily_transactions if t.type == 'expense')
                daily_net = daily_income - daily_expense
                running_balance += daily_net
                
                cash_flow.append({
                    'date': current_date.isoformat(),
                    'income': float(daily_income),
                    'expense': float(daily_expense),
                    'net_flow': float(daily_net),
                    'running_balance': float(running_balance),
                    'transaction_count': len(daily_transactions)
                })
                
                current_date += timedelta(days=1)
            
            return {
                'success': True,
                'cash_flow': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'days': period_days
                    },
                    'final_balance': float(running_balance),
                    'daily_flow': cash_flow
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Nakit akışı hesaplanırken hata: {str(e)}',
                'cash_flow': None
            }
    
    @staticmethod
    def get_customer_analysis(customer_id: int = None) -> Dict[str, Any]:
        """
        Müşteri bazlı finansal analiz
        
        Args:
            customer_id: Müşteri ID (isteğe bağlı)
            
        Returns:
            Dict: Müşteri analiz bilgileri
        """
        try:
            if customer_id:
                # Belirli müşteri analizi
                customer = db.session.get(Customer, customer_id)
                if not customer:
                    return {
                        'success': False,
                        'message': 'Müşteri bulunamadı',
                        'analysis': None
                    }
                
                invoices = db.session.query(Invoice).filter_by(customer_id=customer_id).all()
                
                total_invoices = len(invoices)
                total_amount = sum(invoice.total_amount for invoice in invoices)
                pending_invoices = len([inv for inv in invoices if inv.status == 'pending'])
                paid_invoices = len([inv for inv in invoices if inv.status == 'paid'])
                
                return {
                    'success': True,
                    'analysis': {
                        'customer': customer.to_dict(),
                        'invoice_summary': {
                            'total_invoices': total_invoices,
                            'total_amount': float(total_amount),
                            'pending_invoices': pending_invoices,
                            'paid_invoices': paid_invoices,
                            'average_invoice_amount': float(total_amount / total_invoices) if total_invoices > 0 else 0.0
                        },
                        'invoices': [inv.to_dict() for inv in invoices]
                    }
                }
            else:
                # Tüm müşteriler analizi
                customers_with_invoices = db.session.query(
                    Customer,
                    func.count(Invoice.id).label('invoice_count'),
                    func.sum(Invoice.total_amount).label('total_amount')
                ).outerjoin(Invoice).group_by(Customer.id).all()
                
                customer_analysis = []
                for customer, invoice_count, total_amount in customers_with_invoices:
                    customer_analysis.append({
                        'customer': customer.to_dict(),
                        'invoice_count': invoice_count or 0,
                        'total_amount': float(total_amount or 0),
                        'average_invoice': float((total_amount or 0) / invoice_count) if invoice_count else 0.0
                    })
                
                return {
                    'success': True,
                    'analysis': {
                        'total_customers': len(customer_analysis),
                        'customers': customer_analysis
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Müşteri analizi yapılırken hata: {str(e)}',
                'analysis': None
            }
    
    @staticmethod
    def get_invoice_status_summary() -> Dict[str, Any]:
        """
        Fatura durum özeti
        
        Returns:
            Dict: Fatura durum bilgileri
        """
        try:
            status_summary = db.session.query(
                Invoice.status,
                func.count(Invoice.id).label('count'),
                func.sum(Invoice.total_amount).label('total_amount')
            ).group_by(Invoice.status).all()
            
            summary = {}
            total_invoices = 0
            total_amount = 0.0
            
            for status, count, amount in status_summary:
                summary[status] = {
                    'count': count,
                    'total_amount': float(amount or 0)
                }
                total_invoices += count
                total_amount += float(amount or 0)
            
            return {
                'success': True,
                'invoice_summary': {
                    'by_status': summary,
                    'totals': {
                        'total_invoices': total_invoices,
                        'total_amount': total_amount
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Fatura özeti hesaplanırken hata: {str(e)}',
                'invoice_summary': None
            }
    
    @staticmethod
    def get_profit_loss_statement(start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Kar-zarar tablosu
        
        Args:
            start_date: Başlangıç tarihi (YYYY-MM-DD)
            end_date: Bitiş tarihi (YYYY-MM-DD)
            
        Returns:
            Dict: Kar-zarar tablosu
        """
        try:
            # Eğer tarih belirtilmemişse, bu ayı kullan
            if not start_date or not end_date:
                today = datetime.now().date()
                start_date = today.replace(day=1).isoformat()
                end_date = today.isoformat()
            
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Gelirler (faturalardan)
            paid_invoices = db.session.query(Invoice).filter(
                and_(
                    Invoice.status == 'paid',
                    Invoice.date >= start_date_obj,
                    Invoice.date <= end_date_obj
                )
            ).all()
            
            total_revenue = sum(invoice.total_amount for invoice in paid_invoices)
            
            # Giderler (expense tipindeki işlemlerden)
            expenses = db.session.query(Transaction).filter(
                and_(
                    Transaction.type == 'expense',
                    Transaction.date >= start_date_obj,
                    Transaction.date <= end_date_obj
                )
            ).all()
            
            total_expenses = sum(expense.amount for expense in expenses)
            
            # Kar/zarar hesaplama
            gross_profit = total_revenue - total_expenses
            net_profit = gross_profit  # Şimdilik basit hesaplama
            
            return {
                'success': True,
                'profit_loss': {
                    'period': {
                        'start_date': start_date,
                        'end_date': end_date
                    },
                    'revenue': {
                        'total_revenue': float(total_revenue),
                        'invoice_count': len(paid_invoices)
                    },
                    'expenses': {
                        'total_expenses': float(total_expenses),
                        'expense_count': len(expenses)
                    },
                    'profit': {
                        'gross_profit': float(gross_profit),
                        'net_profit': float(net_profit),
                        'profit_margin': float((net_profit / total_revenue * 100)) if total_revenue > 0 else 0.0
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Kar-zarar tablosu oluşturulurken hata: {str(e)}',
                'profit_loss': None
            }
    
    @staticmethod
    def get_transaction_summary_by_type() -> Dict[str, Any]:
        """
        İşlem tipine göre özet
        
        Returns:
            Dict: İşlem tipi özeti
        """
        try:
            type_summary = db.session.query(
                Transaction.type,
                func.count(Transaction.id).label('count'),
                func.sum(Transaction.amount).label('total_amount'),
                func.avg(Transaction.amount).label('average_amount')
            ).group_by(Transaction.type).all()
            
            summary = {}
            for transaction_type, count, total_amount, average_amount in type_summary:
                summary[transaction_type] = {
                    'count': count,
                    'total_amount': float(total_amount or 0),
                    'average_amount': float(average_amount or 0)
                }
            
            return {
                'success': True,
                'transaction_summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'İşlem özeti hesaplanırken hata: {str(e)}',
                'transaction_summary': None
            }
