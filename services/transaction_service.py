from models.transaction import Transaction, db
from models.invoice import Invoice
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from typing import List, Optional, Dict, Any


class TransactionService:
    
    @staticmethod
    def create_transaction(invoice_id: int, amount: float, date: str, type: str) -> Dict[str, Any]:
        """
        Create new transaction
        
        Args:
            invoice_id: Invoice ID
            amount: Amount
            date: Transaction date (YYYY-MM-DD format)
            type: Transaction type
            
        Returns:
            Dict: Operation result and transaction information
        """
        try:
            invoice = db.session.get(Invoice, invoice_id)
            if not invoice:
                return {
                    'success': False,
                    'message': 'Invoice not found',
                    'transaction': None
                }
            
            try:
                transaction_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return {
                    'success': False,
                    'message': 'Invalid date format. Must be YYYY-MM-DD',
                    'transaction': None
                }
            
            transaction = Transaction(
                invoice_id=invoice_id,
                amount=amount,
                date=transaction_date,
                type=type
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Transaction created successfully',
                'transaction': transaction.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating transaction: {str(e)}',
                'transaction': None
            }
    
    @staticmethod
    def get_transaction_by_id(transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        try:
            return db.session.get(Transaction, transaction_id)
        except Exception:
            return None
    
    @staticmethod
    def get_all_transactions(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get all transactions paginated
        
        Args:
            page: Page number
            per_page: Number of records per page
            
        Returns:
            Dict: Transactions and pagination information
        """
        try:
            transactions = Transaction.query.order_by(Transaction.date.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'transactions': [transaction.to_dict() for transaction in transactions.items],
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting transactions: {str(e)}',
                'transactions': []
            }
    
    @staticmethod
    def get_transactions_by_invoice(invoice_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get transactions by invoice
        
        Args:
            invoice_id: Invoice ID
            page: Page number
            per_page: Number of records per page
            
        Returns:
            Dict: Invoice's transactions
        """
        try:
            invoice = db.session.get(Invoice, invoice_id)
            if not invoice:
                return {
                    'success': False,
                    'message': 'Invoice not found',
                    'transactions': []
                }
            
            transactions = Transaction.query.filter_by(invoice_id=invoice_id).order_by(Transaction.date.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'transactions': [transaction.to_dict() for transaction in transactions.items],
                'invoice': invoice.to_dict(),
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting transactions by invoice: {str(e)}',
                'transactions': []
            }
    
    @staticmethod
    def get_transactions_by_type(type: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get transactions by type
        
        Args:
            type: Transaction type
            page: Page number
            per_page: Number of records per page
            
        Returns:
            Dict: Transactions by type
        """
        try:
            transactions = Transaction.query.filter_by(type=type).order_by(Transaction.date.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'transactions': [transaction.to_dict() for transaction in transactions.items],
                'type': type,
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting transactions by type: {str(e)}',
                'transactions': []
            }
    
    @staticmethod
    def update_transaction(transaction_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update transaction information
        
        Args:
            transaction_id: Transaction ID
            **kwargs: Fields to update
            
        Returns:
            Dict: Operation result
        """
        try:
            transaction = TransactionService.get_transaction_by_id(transaction_id)
            if not transaction:
                return {
                    'success': False,
                    'message': 'Transaction not found',
                    'transaction': None
                }
            
            for key, value in kwargs.items():
                if hasattr(transaction, key) and key != 'id':
                    if key == 'invoice_id':
                        invoice = db.session.get(Invoice, value)
                        if not invoice:
                            return {
                                'success': False,
                                'message': 'Invalid invoice ID',
                                'transaction': None
                            }
                        setattr(transaction, key, value)
                    elif key == 'date':
                        try:
                            if isinstance(value, str):
                                transaction_date = datetime.strptime(value, '%Y-%m-%d').date()
                                setattr(transaction, key, transaction_date)
                            else:
                                setattr(transaction, key, value)
                        except ValueError:
                            return {
                                'success': False,
                                'message': 'Invalid date format. Must be YYYY-MM-DD',
                                'transaction': None
                            }
                    else:
                        setattr(transaction, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Transaction updated successfully',
                'transaction': transaction.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating transaction: {str(e)}',
                'transaction': None
            }
    
    @staticmethod
    def delete_transaction(transaction_id: int) -> Dict[str, Any]:
        """
        Delete transaction
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Dict: Operation result
        """
        try:
            transaction = TransactionService.get_transaction_by_id(transaction_id)
            if not transaction:
                return {
                    'success': False,
                    'message': 'Transaction not found'
                }
            
            db.session.delete(transaction)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Transaction deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting transaction: {str(e)}'
            }
    
    @staticmethod
    def get_transaction_statistics() -> Dict[str, Any]:
        """
        Get transaction statistics
        
        Returns:
            Dict: Statistics information
        """
        try:
            total_transactions = Transaction.query.count()
            
            total_amount = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
            
            types_stats = db.session.query(
                Transaction.type,
                db.func.count(Transaction.id).label('count'),
                db.func.sum(Transaction.amount).label('total_amount')
            ).group_by(Transaction.type).all()
            
            types_info = {}
            for type_stat in types_stats:
                types_info[type_stat.type] = {
                    'count': type_stat.count,
                    'total_amount': float(type_stat.total_amount or 0)
                }
            
            monthly_stats = db.session.query(
                db.func.strftime('%Y-%m', Transaction.date).label('month'),
                db.func.count(Transaction.id).label('count'),
                db.func.sum(Transaction.amount).label('total_amount')
            ).group_by(db.func.strftime('%Y-%m', Transaction.date)).order_by('month').limit(12).all()
            
            monthly_info = {}
            for month_stat in monthly_stats:
                monthly_info[month_stat.month] = {
                    'count': month_stat.count,
                    'total_amount': float(month_stat.total_amount or 0)
                }
            
            return {
                'success': True,
                'statistics': {
                    'total_transactions': total_transactions,
                    'total_amount': float(total_amount),
                    'by_type': types_info,
                    'monthly': monthly_info
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting statistics: {str(e)}',
                'statistics': {}
            }
    
    @staticmethod
    def search_transactions(query: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Search transactions by type or amount
        
        Args:
            query: Search query
            page: Page number
            per_page: Number of records per page
            
        Returns:
            Dict: Search results
        """
        try:
            search_pattern = f"%{query.lower()}%"
            
            transactions = Transaction.query.filter(
                db.or_(
                    Transaction.type.ilike(search_pattern),
                    db.cast(Transaction.amount, db.String).like(search_pattern)
                )
            ).order_by(Transaction.date.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'transactions': [transaction.to_dict() for transaction in transactions.items],
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': page,
                'per_page': per_page,
                'query': query
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error searching transactions: {str(e)}',
                'transactions': []
            }
