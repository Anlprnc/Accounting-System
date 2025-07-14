from models.invoice import Invoice, db
from models.customer import Customer
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from typing import List, Optional, Dict, Any


class InvoiceService:
    
    @staticmethod
    def create_invoice(customer_id: int, date: str, total_amount: float, status: str = 'pending') -> Dict[str, Any]:
        """
        Create new invoice
        
        Args:
            customer_id: Customer ID
            date: Invoice date (YYYY-MM-DD format)
            total_amount: Total amount
            status: Status (default: 'pending')
            
        Returns:
            Dict: Operation result and invoice information
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return {
                    'success': False,
                    'message': 'Customer not found',
                    'invoice': None
                }
            
            try:
                invoice_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return {
                    'success': False,
                    'message': 'Invalid date format. Must be YYYY-MM-DD',
                    'invoice': None
                }
            
            allowed_statuses = ['pending', 'paid', 'cancelled', 'overdue']
            if status not in allowed_statuses:
                status = 'pending'
            
            invoice = Invoice(
                customer_id=customer_id,
                date=invoice_date,
                total_amount=total_amount,
                status=status
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Invoice created successfully',
                'invoice': invoice.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating invoice: {str(e)}',
                'invoice': None
            }
    
    @staticmethod
    def get_invoice_by_id(invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        try:
            return db.session.get(Invoice, invoice_id)
        except Exception:
            return None
    
    @staticmethod
    def get_all_invoices(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get all invoices paginated
        
        Args:
            page: Page number
            per_page: Number of records per page
            
        Returns:
            Dict: Invoices and pagination information
        """
        try:
            invoices = Invoice.query.order_by(Invoice.date.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'invoices': [invoice.to_dict() for invoice in invoices.items],
                'total': invoices.total,
                'pages': invoices.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting invoices: {str(e)}',
                'invoices': []
            }
    
    @staticmethod
    def get_invoices_by_customer(customer_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get invoices by customer
        
        Args:
            customer_id: Customer ID
            page: Page number
            per_page: Number of records per page
            
        Returns:
            Dict: Customer's invoices
        """
        try:
            customer = Customer.query.get(customer_id)
            if not customer:
                return {
                    'success': False,
                    'message': 'Customer not found',
                    'invoices': []
                }
            
            invoices = Invoice.query.filter_by(customer_id=customer_id).order_by(Invoice.date.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'invoices': [invoice.to_dict() for invoice in invoices.items],
                'customer': customer.to_dict(),
                'total': invoices.total,
                'pages': invoices.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting invoices by customer: {str(e)}',
                'invoices': []
            }
    
    @staticmethod
    def get_invoices_by_status(status: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get invoices by status
        
        Args:
            status: Invoice status
            page: Page number
            per_page: Number of records per page
            
        Returns:
            Dict: Invoices by status
        """
        try:
            allowed_statuses = ['pending', 'paid', 'cancelled', 'overdue']
            if status not in allowed_statuses:
                return {
                    'success': False,
                    'message': f'Invalid status. Allowed values: {", ".join(allowed_statuses)}',
                    'invoices': []
                }
            
            invoices = Invoice.query.filter_by(status=status).order_by(Invoice.date.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'invoices': [invoice.to_dict() for invoice in invoices.items],
                'status': status,
                'total': invoices.total,
                'pages': invoices.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting invoices by status: {str(e)}',
                'invoices': []
            }
    
    @staticmethod
    def update_invoice(invoice_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update invoice information
        
        Args:
            invoice_id: Invoice ID
            **kwargs: Fields to update
            
        Returns:
            Dict: Operation result
        """
        try:
            invoice = InvoiceService.get_invoice_by_id(invoice_id)
            if not invoice:
                return {
                    'success': False,
                    'message': 'Invoice not found',
                    'invoice': None
                }
            
            for key, value in kwargs.items():
                if hasattr(invoice, key) and key != 'id':
                    if key == 'customer_id':
                        customer = Customer.query.get(value)
                        if not customer:
                            return {
                                'success': False,
                                'message': 'Invalid customer ID',
                                'invoice': None
                            }
                        setattr(invoice, key, value)
                    elif key == 'date':
                        try:
                            if isinstance(value, str):
                                invoice_date = datetime.strptime(value, '%Y-%m-%d').date()
                                setattr(invoice, key, invoice_date)
                            else:
                                setattr(invoice, key, value)
                        except ValueError:
                            return {
                                'success': False,
                                'message': 'Invalid date format. Must be YYYY-MM-DD',
                                'invoice': None
                            }
                    elif key == 'status':
                        allowed_statuses = ['pending', 'paid', 'cancelled', 'overdue']
                        if value in allowed_statuses:
                            setattr(invoice, key, value)
                    else:
                        setattr(invoice, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Invoice updated successfully',
                'invoice': invoice.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating invoice: {str(e)}',
                'invoice': None
            }
    
    @staticmethod
    def delete_invoice(invoice_id: int) -> Dict[str, Any]:
        """
        Delete invoice
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Dict: Operation result
        """
        try:
            invoice = InvoiceService.get_invoice_by_id(invoice_id)
            if not invoice:
                return {
                    'success': False,
                    'message': 'Invoice not found'
                }
            
            db.session.delete(invoice)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Invoice deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting invoice: {str(e)}'
            }
    
    @staticmethod
    def update_invoice_status(invoice_id: int, status: str) -> Dict[str, Any]:
        """
        Update invoice status
        
        Args:
            invoice_id: Invoice ID
            status: New status
            
        Returns:
            Dict: Operation result
        """
        try:
            allowed_statuses = ['pending', 'paid', 'cancelled', 'overdue']
            if status not in allowed_statuses:
                return {
                    'success': False,
                    'message': f'Invalid status. Allowed values: {", ".join(allowed_statuses)}',
                    'invoice': None
                }
            
            invoice = InvoiceService.get_invoice_by_id(invoice_id)
            if not invoice:
                return {
                    'success': False,
                    'message': 'Invoice not found',
                    'invoice': None
                }
            
            invoice.status = status
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Invoice status updated to "{status}"',
                'invoice': invoice.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating invoice status: {str(e)}',
                'invoice': None
            }
    
    @staticmethod
    def get_invoice_statistics() -> Dict[str, Any]:
        """
        Get invoice statistics
        
        Returns:
            Dict: Statistics information
        """
        try:
            total_invoices = Invoice.query.count()
            pending_invoices = Invoice.query.filter_by(status='pending').count()
            paid_invoices = Invoice.query.filter_by(status='paid').count()
            cancelled_invoices = Invoice.query.filter_by(status='cancelled').count()
            overdue_invoices = Invoice.query.filter_by(status='overdue').count()
            
            total_amount = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
            paid_amount = db.session.query(db.func.sum(Invoice.total_amount)).filter_by(status='paid').scalar() or 0
            pending_amount = db.session.query(db.func.sum(Invoice.total_amount)).filter_by(status='pending').scalar() or 0
            
            return {
                'success': True,
                'statistics': {
                    'total_invoices': total_invoices,
                    'pending_invoices': pending_invoices,
                    'paid_invoices': paid_invoices,
                    'cancelled_invoices': cancelled_invoices,
                    'overdue_invoices': overdue_invoices,
                    'total_amount': total_amount,
                    'paid_amount': paid_amount,
                    'pending_amount': pending_amount
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting statistics: {str(e)}',
                'statistics': {}
            }
