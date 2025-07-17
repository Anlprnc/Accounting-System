import pytest
from datetime import date
from services.user_service import UserService
from services.accounting_service import AccountingService
from services.invoice_service import InvoiceService
from services.transaction_service import TransactionService
from models.user import User, db
from models.customer import Customer
from models.invoice import Invoice
from models.transaction import Transaction


class TestUserService:
    
    def test_create_user_success(self, app):
        with app.app_context():
            result = UserService.create_user(
                fullname="John Doe",
                email="john.doe@example.com",
                password="password123",
                role="user"
            )
            
            assert result['success'] is True
            assert result['message'] == "User created successfully"
            assert result['user'] is not None
            assert result['user']['email'] == "john.doe@example.com"
            assert result['user']['role'] == "user"
    
    def test_create_user_role_enforcement(self, app):
        with app.app_context():
            result = UserService.create_user(
                fullname="Admin User",
                email="admin.user@example.com",
                password="password123",
                role="admin"
            )
            
            assert result['success'] is True
            assert result['user']['role'] == "user"
    
    def test_create_user_invalid_role(self, app):
        with app.app_context():
            result = UserService.create_user(
                fullname="Test User",
                email="test.role@example.com",
                password="password123",
                role="superuser"
            )
            
            assert result['success'] is True
            assert result['user']['role'] == "user"
    
    def test_create_user_duplicate_email(self, app):
        with app.app_context():
            UserService.create_user(
                fullname="First User",
                email="duplicate@example.com",
                password="password123"
            )
            
            result = UserService.create_user(
                fullname="Second User",
                email="duplicate@example.com",
                password="password456"
            )
            
            assert result['success'] is False
            assert "already in use" in result['message']
            assert result['user'] is None
    
    def test_create_admin_user(self, app):
        with app.app_context():
            result = UserService.create_admin_user(
                fullname="Admin User",
                email="new.admin@example.com",
                password="admin123"
            )
            
            assert result['success'] is True
            assert result['message'] == "Admin user created successfully"
            assert result['user']['role'] == "admin"
    
    def test_get_user_by_id(self, app):
        with app.app_context():
            create_result = UserService.create_user(
                fullname="Test User",
                email="getbyid@example.com",
                password="password123"
            )
            
            user_id = create_result['user']['id']
            
            user = UserService.get_user_by_id(user_id)
            
            assert user is not None
            assert user.email == "getbyid@example.com"
            assert user.fullname == "Test User"
    
    def test_get_user_by_id_not_found(self, app):
        with app.app_context():
            user = UserService.get_user_by_id(99999)
            assert user is None
    
    def test_get_user_by_email(self, app):
        with app.app_context():
            UserService.create_user(
                fullname="Email Test",
                email="emailtest@example.com",
                password="password123"
            )
            
            user = UserService.get_user_by_email("emailtest@example.com")
            
            assert user is not None
            assert user.fullname == "Email Test"
    
    def test_get_user_by_email_case_insensitive(self, app):
        with app.app_context():
            UserService.create_user(
                fullname="Case Test",
                email="case@example.com",
                password="password123"
            )
            
            user1 = UserService.get_user_by_email("CASE@EXAMPLE.COM")
            user2 = UserService.get_user_by_email("Case@Example.Com")
            
            assert user1 is not None
            assert user2 is not None
            assert user1.id == user2.id
    
    def test_authenticate_user_success(self, app):
        with app.app_context():
            UserService.create_user(
                fullname="Auth User",
                email="auth@example.com",
                password="password123"
            )
            
            result = UserService.authenticate_user(
                email="auth@example.com",
                password="password123"
            )
            
            assert result['success'] is True
            assert result['message'] == "Login successful"
            assert result['user'] is not None
            assert result['user']['email'] == "auth@example.com"
    
    def test_authenticate_user_wrong_password(self, app):
        with app.app_context():
            UserService.create_user(
                fullname="Auth User",
                email="auth2@example.com",
                password="password123"
            )
            
            result = UserService.authenticate_user(
                email="auth2@example.com",
                password="wrongpassword"
            )
            
            assert result['success'] is False
            assert "incorrect" in result['message'].lower()
            assert result['user'] is None
    
    def test_authenticate_user_not_found(self, app):
        with app.app_context():
            result = UserService.authenticate_user(
                email="nonexistent@example.com",
                password="password123"
            )
            
            assert result['success'] is False
            assert "incorrect" in result['message'].lower()
            assert result['user'] is None
    
    def test_update_user_success(self, app):
        with app.app_context():
            create_result = UserService.create_user(
                fullname="Update User",
                email="update@example.com",
                password="password123"
            )
            
            user_id = create_result['user']['id']
            
            result = UserService.update_user(
                user_id=user_id,
                fullname="Updated Name",
                email="updated@example.com"
            )
            
            assert result['success'] is True
            assert result['user']['fullname'] == "Updated Name"
            assert result['user']['email'] == "updated@example.com"
    
    def test_update_user_password(self, app):
        with app.app_context():
            create_result = UserService.create_user(
                fullname="Password User",
                email="password@example.com",
                password="oldpassword"
            )
            
            user_id = create_result['user']['id']
            
            result = UserService.update_user(
                user_id=user_id,
                password="newpassword"
            )
            
            assert result['success'] is True
            
            auth_result = UserService.authenticate_user(
                email="password@example.com",
                password="newpassword"
            )
            assert auth_result['success'] is True
    
    def test_update_user_duplicate_email(self, app):
        with app.app_context():
            UserService.create_user("User 1", "user1@example.com", "password")
            create_result = UserService.create_user("User 2", "user2@example.com", "password")
            
            user_id = create_result['user']['id']
            
            result = UserService.update_user(
                user_id=user_id,
                email="user1@example.com"
            )
            
            assert result['success'] is False
            assert "already in use" in result['message']
    
    def test_change_password_success(self, app):
        with app.app_context():
            create_result = UserService.create_user(
                fullname="Change Password User",
                email="changepwd@example.com",
                password="oldpassword"
            )
            
            user_id = create_result['user']['id']
            
            result = UserService.change_password(
                user_id=user_id,
                current_password="oldpassword",
                new_password="newpassword"
            )
            
            assert result['success'] is True
            assert result['message'] == "Password changed successfully"
    
    def test_change_password_wrong_current(self, app):
        with app.app_context():
            create_result = UserService.create_user(
                fullname="Wrong Password User",
                email="wrongpwd@example.com",
                password="password123"
            )
            
            user_id = create_result['user']['id']
            
            result = UserService.change_password(
                user_id=user_id,
                current_password="wrongpassword",
                new_password="newpassword"
            )
            
            assert result['success'] is False
            assert "incorrect" in result['message'].lower()
    
    def test_delete_user_success(self, app):
        with app.app_context():
            create_result = UserService.create_user(
                fullname="Delete User",
                email="delete@example.com",
                password="password123"
            )
            
            user_id = create_result['user']['id']
            
            result = UserService.delete_user(user_id)
            
            assert result['success'] is True
            assert result['message'] == "User deleted successfully"
            
            user = UserService.get_user_by_id(user_id)
            assert user is None
    
    def test_delete_user_not_found(self, app):
        with app.app_context():
            result = UserService.delete_user(99999)
            
            assert result['success'] is False
            assert "not found" in result['message'].lower()
    
    def test_get_users_by_role(self, app):
        with app.app_context():
            UserService.create_user("User 1", "user1@role.com", "password", "user")
            UserService.create_user("User 2", "user2@role.com", "password", "user")
            UserService.create_admin_user("Admin 1", "admin1@role.com", "password")
            
            users = UserService.get_users_by_role("user")
            admins = UserService.get_users_by_role("admin")
            
            assert len(users) >= 2
            assert len(admins) >= 1
    
    def test_search_users(self, app):
        with app.app_context():
            UserService.create_user("John Smith", "john.smith@search.com", "password")
            UserService.create_user("Jane Doe", "jane.doe@search.com", "password")
            UserService.create_user("Bob Johnson", "bob@search.com", "password")
            
            result = UserService.search_users("John")
            assert result['success'] is True
            assert len(result['users']) >= 1
            
            result = UserService.search_users("jane.doe")
            assert result['success'] is True
            assert len(result['users']) >= 1
            
            result = UserService.search_users("nonexistent")
            assert result['success'] is True
            assert len(result['users']) == 0


class TestAccountingServiceIntegration:
    """Integration tests for AccountingService using existing test data"""
    
    def test_get_financial_summary_with_test_data(self, app):
        """Test financial summary with the test data from conftest"""
        with app.app_context():
            result = AccountingService.get_financial_summary()
            
            assert result['success'] is True
            assert 'summary' in result
            assert result['summary']['total_income'] >= 0
            assert result['summary']['total_expense'] >= 0
            assert 'net_profit' in result['summary']
    
    def test_get_customer_analysis_integration(self, app):
        """Test customer analysis with real test data"""
        with app.app_context():
            result = AccountingService.get_customer_analysis()
            
            assert result['success'] is True
            assert 'analysis' in result
            assert result['analysis']['total_customers'] == 2
    
    def test_get_invoice_status_summary_integration(self, app):
        """Test invoice status summary with real test data"""
        with app.app_context():
            result = AccountingService.get_invoice_status_summary()
            
            assert result['success'] is True
            assert 'invoice_summary' in result
            assert 'by_status' in result['invoice_summary']
    
    def test_transaction_summary_integration(self, app):
        """Test transaction summary with real test data"""
        with app.app_context():
            result = AccountingService.get_transaction_summary_by_type()
            
            assert result['success'] is True


class TestInvoiceService:
    
    def test_create_invoice_success(self, app):
        """Test successful invoice creation"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            result = InvoiceService.create_invoice(
                customer_id=customer.id,
                date='2024-01-15',
                total_amount=1500.50,
                status='pending'
            )
            
            assert result['success'] is True
            assert result['message'] == 'Fatura başarıyla oluşturuldu'
            assert result['invoice'] is not None
            assert result['invoice']['customer_id'] == customer.id
            assert result['invoice']['total_amount'] == 1500.50
            assert result['invoice']['status'] == 'pending'
    
    def test_create_invoice_invalid_customer(self, app):
        """Test invoice creation with invalid customer"""
        with app.app_context():
            result = InvoiceService.create_invoice(
                customer_id=999,  # Non-existent customer
                date='2024-01-15',
                total_amount=1500.50,
                status='pending'
            )
            
            assert result['success'] is False
            assert result['message'] == 'Müşteri bulunamadı'
            assert result['invoice'] is None
    
    def test_create_invoice_invalid_date(self, app):
        """Test invoice creation with invalid date format"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            result = InvoiceService.create_invoice(
                customer_id=customer.id,
                date='invalid-date',
                total_amount=1500.50,
                status='pending'
            )
            
            assert result['success'] is False
            assert 'Geçersiz tarih formatı' in result['message']
            assert result['invoice'] is None
    
    def test_create_invoice_invalid_status(self, app):
        """Test invoice creation with invalid status (should default to pending)"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            result = InvoiceService.create_invoice(
                customer_id=customer.id,
                date='2024-01-15',
                total_amount=1500.50,
                status='invalid_status'
            )
            
            assert result['success'] is True
            assert result['invoice']['status'] == 'pending'
    
    def test_get_invoice_by_id_success(self, app):
        """Test getting invoice by ID"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.get_invoice_by_id(invoice.id)
            
            assert result is not None
            assert result.id == invoice.id
            assert result.total_amount == 1500.50
    
    def test_get_invoice_by_id_not_found(self, app):
        """Test getting non-existent invoice by ID"""
        with app.app_context():
            result = InvoiceService.get_invoice_by_id(999)
            assert result is None
    
    def test_get_all_invoices(self, app):
        """Test getting all invoices with pagination"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            for i in range(3):
                invoice = Invoice(
                    customer_id=customer.id,
                    date=date(2024, 1, 15),
                    total_amount=1000 + i * 100,
                    status='pending'
                )
                db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.get_all_invoices(page=1, per_page=10)
            
            assert result['success'] is True
            assert len(result['invoices']) >= 3
            assert 'total' in result
            assert 'pages' in result
            assert result['current_page'] == 1
    
    def test_get_invoices_by_customer(self, app):
        """Test getting invoices by customer"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.get_invoices_by_customer(customer.id)
            
            assert result['success'] is True
            assert len(result['invoices']) >= 1
            assert result['customer']['id'] == customer.id
            assert result['invoices'][0]['customer_id'] == customer.id
    
    def test_get_invoices_by_customer_invalid(self, app):
        """Test getting invoices by non-existent customer"""
        with app.app_context():
            result = InvoiceService.get_invoices_by_customer(999)
            
            assert result['success'] is False
            assert result['message'] == 'Müşteri bulunamadı'
            assert result['invoices'] == []
    
    def test_get_invoices_by_status(self, app):
        """Test getting invoices by status"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            statuses = ['pending', 'paid', 'cancelled']
            for status in statuses:
                invoice = Invoice(
                    customer_id=customer.id,
                    date=date(2024, 1, 15),
                    total_amount=1500.50,
                    status=status
                )
                db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.get_invoices_by_status('pending')
            
            assert result['success'] is True
            assert len(result['invoices']) >= 1
            assert result['status'] == 'pending'
            for invoice in result['invoices']:
                assert invoice['status'] == 'pending'
    
    def test_get_invoices_by_status_invalid(self, app):
        """Test getting invoices by invalid status"""
        with app.app_context():
            result = InvoiceService.get_invoices_by_status('invalid_status')
            
            assert result['success'] is False
            assert 'Geçersiz durum' in result['message']
            assert result['invoices'] == []
    
    def test_update_invoice_success(self, app):
        """Test successful invoice update"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.update_invoice(
                invoice.id,
                total_amount=2000.00,
                status='paid'
            )
            
            assert result['success'] is True
            assert result['message'] == 'Fatura başarıyla güncellendi'
            assert result['invoice']['total_amount'] == 2000.00
            assert result['invoice']['status'] == 'paid'
    
    def test_update_invoice_not_found(self, app):
        """Test updating non-existent invoice"""
        with app.app_context():
            result = InvoiceService.update_invoice(999, total_amount=2000.00)
            
            assert result['success'] is False
            assert result['message'] == 'Fatura bulunamadı'
            assert result['invoice'] is None
    
    def test_update_invoice_status_success(self, app):
        """Test successful invoice status update"""
        with app.app_context(): 
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.update_invoice_status(invoice.id, 'paid')
            
            assert result['success'] is True
            assert 'paid' in result['message']
            assert result['invoice']['status'] == 'paid'
    
    def test_update_invoice_status_invalid(self, app):
        """Test updating invoice status with invalid status"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.update_invoice_status(invoice.id, 'invalid_status')
            
            assert result['success'] is False
            assert 'Geçersiz durum' in result['message']
    
    def test_delete_invoice_success(self, app):
        """Test successful invoice deletion"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            invoice_id = invoice.id
            result = InvoiceService.delete_invoice(invoice_id)
            
            assert result['success'] is True
            assert result['message'] == 'Fatura başarıyla silindi'
            
            deleted_invoice = InvoiceService.get_invoice_by_id(invoice_id)
            assert deleted_invoice is None
    
    def test_delete_invoice_not_found(self, app):
        """Test deleting non-existent invoice"""
        with app.app_context():
            result = InvoiceService.delete_invoice(999)
            
            assert result['success'] is False
            assert result['message'] == 'Fatura bulunamadı'
    
    def test_get_invoice_statistics(self, app):
        """Test getting invoice statistics"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            statuses = ['pending', 'paid', 'cancelled', 'overdue']
            amounts = [1000, 2000, 1500, 500]
            
            for status, amount in zip(statuses, amounts):
                invoice = Invoice(
                    customer_id=customer.id,
                    date=date(2024, 1, 15),
                    total_amount=amount,
                    status=status
                )
                db.session.add(invoice)
            db.session.commit()
            
            result = InvoiceService.get_invoice_statistics()
            
            assert result['success'] is True
            assert 'statistics' in result
            stats = result['statistics']
            
            assert 'total_invoices' in stats
            assert 'pending_invoices' in stats
            assert 'paid_invoices' in stats
            assert 'cancelled_invoices' in stats
            assert 'overdue_invoices' in stats
            assert 'total_amount' in stats
            assert 'paid_amount' in stats
            assert 'pending_amount' in stats
            
            assert stats['total_invoices'] >= 4
            assert stats['paid_amount'] >= 2000


class TestTransactionService:
    
    def test_create_transaction_success(self, app):
        """Test successful transaction creation"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            result = TransactionService.create_transaction(
                invoice_id=invoice.id,
                amount=500.0,
                date="2024-01-15",
                type="payment"
            )
            
            assert result['success'] is True
            assert result['message'] == "Transaction created successfully"
            assert result['transaction'] is not None
            assert result['transaction']['amount'] == 500.0
            assert result['transaction']['type'] == "payment"
    
    def test_create_transaction_invalid_invoice(self, app):
        """Test transaction creation with invalid invoice ID"""
        with app.app_context():
            result = TransactionService.create_transaction(
                invoice_id=999,
                amount=500.0,
                date="2024-01-15",
                type="payment"
            )
            
            assert result['success'] is False
            assert result['message'] == "Invoice not found"
            assert result['transaction'] is None
    
    def test_create_transaction_invalid_date(self, app):
        """Test transaction creation with invalid date format"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            result = TransactionService.create_transaction(
                invoice_id=invoice.id,
                amount=500.0,
                date="invalid-date",
                type="payment"
            )
            
            assert result['success'] is False
            assert "Invalid date format" in result['message']
            assert result['transaction'] is None
    
    def test_get_transaction_by_id(self, app):
        """Test getting transaction by ID"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            transaction = Transaction(
                invoice_id=invoice.id,
                amount=500.0,
                date=date(2024, 1, 15),
                type="payment"
            )
            db.session.add(transaction)
            db.session.commit()
            
            result = TransactionService.get_transaction_by_id(transaction.id)
            
            assert result is not None
            assert result.amount == 500.0
            assert result.type == "payment"
    
    def test_get_transaction_by_id_not_found(self, app):
        """Test getting transaction with non-existent ID"""
        with app.app_context():
            result = TransactionService.get_transaction_by_id(999)
            assert result is None
    
    def test_get_all_transactions(self, app):
        """Test getting all transactions with pagination"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            for i in range(3):
                transaction = Transaction(
                    invoice_id=invoice.id,
                    amount=100.0 + i * 50,
                    date=date(2024, 1, 15),
                    type=f"payment{i}"
                )
                db.session.add(transaction)
            db.session.commit()
            
            result = TransactionService.get_all_transactions(page=1, per_page=2)
            
            assert result['success'] is True
            assert 'transactions' in result
            assert 'total' in result
            assert 'pages' in result
            assert result['current_page'] == 1
            assert result['per_page'] == 2
    
    def test_get_transactions_by_invoice(self, app):
        """Test getting transactions by invoice ID"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice1 = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            invoice2 = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 16),
                total_amount=2000.0,
                status='pending'
            )
            db.session.add(invoice1)
            db.session.add(invoice2)
            db.session.commit()
            
            for i in range(2):
                transaction = Transaction(
                    invoice_id=invoice1.id,
                    amount=100.0 + i * 50,
                    date=date(2024, 1, 15),
                    type=f"payment{i}"
                )
                db.session.add(transaction)
            
            transaction = Transaction(
                invoice_id=invoice2.id,
                amount=300.0,
                date=date(2024, 1, 16),
                type="payment"
            )
            db.session.add(transaction)
            db.session.commit()
            
            result = TransactionService.get_transactions_by_invoice(invoice1.id)
            
            assert result['success'] is True
            assert 'transactions' in result
            assert 'invoice' in result
            assert len(result['transactions']) == 2
            assert result['invoice']['id'] == invoice1.id
    
    def test_get_transactions_by_invoice_not_found(self, app):
        """Test getting transactions for non-existent invoice"""
        with app.app_context():
            result = TransactionService.get_transactions_by_invoice(999)
            
            assert result['success'] is False
            assert result['message'] == "Invoice not found"
            assert result['transactions'] == []
    
    def test_get_transactions_by_type(self, app):
        """Test getting transactions by type"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            payment_transaction = Transaction(
                invoice_id=invoice.id,
                amount=100.0,
                date=date(2024, 1, 15),
                type="payment"
            )
            refund_transaction = Transaction(
                invoice_id=invoice.id,
                amount=50.0,
                date=date(2024, 1, 15),
                type="refund"
            )
            db.session.add(payment_transaction)
            db.session.add(refund_transaction)
            db.session.commit()
            
            result = TransactionService.get_transactions_by_type("payment")
            
            assert result['success'] is True
            assert 'transactions' in result
            assert result['type'] == "payment"
            assert len(result['transactions']) >= 1
            assert all(t['type'] == "payment" for t in result['transactions'])
    
    def test_update_transaction_success(self, app):
        """Test successful transaction update"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            transaction = Transaction(
                invoice_id=invoice.id,
                amount=500.0,
                date=date(2024, 1, 15),
                type="payment"
            )
            db.session.add(transaction)
            db.session.commit()
            
            result = TransactionService.update_transaction(
                transaction.id,
                amount=750.0,
                type="refund"
            )
            
            assert result['success'] is True
            assert result['message'] == "Transaction updated successfully"
            assert result['transaction']['amount'] == 750.0
            assert result['transaction']['type'] == "refund"
    
    def test_update_transaction_not_found(self, app):
        """Test updating non-existent transaction"""
        with app.app_context():
            result = TransactionService.update_transaction(999, amount=100.0)
            
            assert result['success'] is False
            assert result['message'] == "Transaction not found"
            assert result['transaction'] is None
    
    def test_update_transaction_invalid_invoice(self, app):
        """Test updating transaction with invalid invoice ID"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            transaction = Transaction(
                invoice_id=invoice.id,
                amount=500.0,
                date=date(2024, 1, 15),
                type="payment"
            )
            db.session.add(transaction)
            db.session.commit()
            
            result = TransactionService.update_transaction(
                transaction.id,
                invoice_id=999
            )
            
            assert result['success'] is False
            assert result['message'] == "Invalid invoice ID"
    
    def test_delete_transaction_success(self, app):
        """Test successful transaction deletion"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            transaction = Transaction(
                invoice_id=invoice.id,
                amount=500.0,
                date=date(2024, 1, 15),
                type="payment"
            )
            db.session.add(transaction)
            db.session.commit()
            
            transaction_id = transaction.id
            
            result = TransactionService.delete_transaction(transaction_id)
            
            assert result['success'] is True
            assert result['message'] == "Transaction deleted successfully"
            
            # Verify deletion
            deleted_transaction = TransactionService.get_transaction_by_id(transaction_id)
            assert deleted_transaction is None
    
    def test_delete_transaction_not_found(self, app):
        """Test deleting non-existent transaction"""
        with app.app_context():
            result = TransactionService.delete_transaction(999)
            
            assert result['success'] is False
            assert result['message'] == "Transaction not found"
    
    def test_get_transaction_statistics(self, app):
        """Test getting transaction statistics"""
        with app.app_context():
            # Create customer and invoice
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            transactions_data = [
                {"amount": 100.0, "type": "payment"},
                {"amount": 200.0, "type": "payment"},
                {"amount": 50.0, "type": "refund"},
            ]
            
            for data in transactions_data:
                transaction = Transaction(
                    invoice_id=invoice.id,
                    amount=data["amount"],
                    date=date(2024, 1, 15),
                    type=data["type"]
                )
                db.session.add(transaction)
            db.session.commit()
            
            result = TransactionService.get_transaction_statistics()
            
            assert result['success'] is True
            assert 'statistics' in result
            stats = result['statistics']
            
            assert 'total_transactions' in stats
            assert 'total_amount' in stats
            assert 'by_type' in stats
            assert 'monthly' in stats
            
            assert stats['total_transactions'] >= 3
            assert stats['total_amount'] >= 350.0
    
    def test_search_transactions(self, app):
        """Test searching transactions"""
        with app.app_context():
            customer = Customer(
                name="Test Customer",
                address="Test Address",
                phone="123456789",
                email="test@customer.com"
            )
            db.session.add(customer)
            db.session.commit()
            
            invoice = Invoice(
                customer_id=customer.id,
                date=date(2024, 1, 15),
                total_amount=1000.0,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            
            payment_transaction = Transaction(
                invoice_id=invoice.id,
                amount=100.0,
                date=date(2024, 1, 15),
                type="payment"
            )
            refund_transaction = Transaction(
                invoice_id=invoice.id,
                amount=50.0,
                date=date(2024, 1, 15),
                type="refund"
            )
            db.session.add(payment_transaction)
            db.session.add(refund_transaction)
            db.session.commit()
            
            result = TransactionService.search_transactions("payment")
            
            assert result['success'] is True
            assert 'transactions' in result
            assert result['query'] == "payment"
            assert len(result['transactions']) >= 1