import pytest
import json
from datetime import date
from models.customer import Customer
from models.invoice import Invoice
from models.transaction import Transaction
from models import db


class TestTransactionRoutes:
    
    def test_get_transactions_requires_auth(self, client):
        """Test that getting transactions requires authentication"""
        response = client.get('/api/transactions/')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'missing' in data['message'].lower()
    
    def test_get_transactions_success(self, client, auth_headers, app):
        """Test successful retrieval of transactions"""
        headers = auth_headers()
        
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
        
        response = client.get('/api/transactions/', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'transactions' in data
        assert 'total' in data
        assert 'pages' in data
    
    def test_get_transactions_pagination(self, client, auth_headers, app):
        """Test transaction pagination"""
        headers = auth_headers()
        
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
            
            for i in range(5):
                transaction = Transaction(
                    invoice_id=invoice.id,
                    amount=100.0 + i * 50,
                    date=date(2024, 1, 15),
                    type=f"payment{i}"
                )
                db.session.add(transaction)
            db.session.commit()
        
        response = client.get('/api/transactions/?page=1&per_page=2', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['current_page'] == 1
        assert data['per_page'] == 2
        assert len(data['transactions']) <= 2
    
    def test_get_transaction_by_id_success(self, client, auth_headers, app):
        """Test getting a specific transaction by ID"""
        headers = auth_headers()
        
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
        
        response = client.get(f'/api/transactions/{transaction_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['transaction']['id'] == transaction_id
        assert data['transaction']['amount'] == 500.0
        assert data['transaction']['type'] == "payment"
    
    def test_get_transaction_by_id_not_found(self, client, auth_headers):
        """Test getting a non-existent transaction"""
        headers = auth_headers()
        
        response = client.get('/api/transactions/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert "not found" in data['message'].lower()
    
    def test_create_transaction_success(self, client, auth_headers, app):
        """Test successful transaction creation"""
        headers = auth_headers()
        
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
            
            invoice_id = invoice.id
        
        transaction_data = {
            'invoice_id': invoice_id,
            'amount': 500.0,
            'date': '2024-01-15',
            'type': 'payment'
        }
        
        response = client.post(
            '/api/transactions/',
            data=json.dumps(transaction_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == "Transaction created successfully"
        assert data['transaction']['amount'] == 500.0
        assert data['transaction']['type'] == "payment"
    
    def test_create_transaction_missing_data(self, client, auth_headers):
        """Test transaction creation with missing data"""
        headers = auth_headers()
        
        response = client.post(
            '/api/transactions/',
            data=json.dumps({}),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert "missing" in data['message'].lower()
    
    def test_create_transaction_missing_required_field(self, client, auth_headers):
        """Test transaction creation with missing required fields"""
        headers = auth_headers()
        
        incomplete_data = {
            'amount': 500.0,
            'date': '2024-01-15'
        }
        
        response = client.post(
            '/api/transactions/',
            data=json.dumps(incomplete_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert "required field" in data['message'].lower()
    
    def test_create_transaction_invalid_invoice(self, client, auth_headers):
        """Test transaction creation with invalid invoice ID"""
        headers = auth_headers()
        
        transaction_data = {
            'invoice_id': 999,
            'amount': 500.0,
            'date': '2024-01-15',
            'type': 'payment'
        }
        
        response = client.post(
            '/api/transactions/',
            data=json.dumps(transaction_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert "not found" in data['message'].lower()
    
    def test_update_transaction_success(self, client, auth_headers, app):
        """Test successful transaction update"""
        headers = auth_headers()
        
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
        
        update_data = {
            'amount': 750.0,
            'type': 'refund'
        }
        
        response = client.put(
            f'/api/transactions/{transaction_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == "Transaction updated successfully"
        assert data['transaction']['amount'] == 750.0
        assert data['transaction']['type'] == "refund"
    
    def test_update_transaction_not_found(self, client, auth_headers):
        """Test updating a non-existent transaction"""
        headers = auth_headers()
        
        update_data = {
            'amount': 750.0
        }
        
        response = client.put(
            '/api/transactions/999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert "not found" in data['message'].lower()
    
    def test_update_transaction_missing_data(self, client, auth_headers, app):
        """Test transaction update with missing data"""
        headers = auth_headers()
        
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
        
        response = client.put(
            f'/api/transactions/{transaction_id}',
            data=json.dumps({}),
            content_type='application/json',
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert "missing" in data['message'].lower()
    
    def test_delete_transaction_success(self, client, auth_headers, app):
        """Test successful transaction deletion"""
        headers = auth_headers()
        
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
        
        response = client.delete(f'/api/transactions/{transaction_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == "Transaction deleted successfully"
        
        get_response = client.get(f'/api/transactions/{transaction_id}', headers=headers)
        assert get_response.status_code == 404
    
    def test_delete_transaction_not_found(self, client, auth_headers):
        """Test deleting a non-existent transaction"""
        headers = auth_headers()
        
        response = client.delete('/api/transactions/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert "not found" in data['message'].lower()
    
    def test_get_transactions_by_invoice(self, client, auth_headers, app):
        """Test getting transactions by invoice ID"""
        headers = auth_headers()
        
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
            
            invoice1_id = invoice1.id
        
        response = client.get(f'/api/transactions/by-invoice/{invoice1_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'transactions' in data
        assert 'invoice' in data
        assert len(data['transactions']) == 2
        assert data['invoice']['id'] == invoice1_id
    
    def test_get_transactions_by_invoice_not_found(self, client, auth_headers):
        """Test getting transactions for non-existent invoice"""
        headers = auth_headers()
        
        response = client.get('/api/transactions/by-invoice/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert "not found" in data['message'].lower()
    
    def test_get_transactions_by_type(self, client, auth_headers, app):
        """Test getting transactions by type"""
        headers = auth_headers()
        
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
        
        response = client.get('/api/transactions/by-type/payment', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'transactions' in data
        assert data['type'] == "payment"
        assert len(data['transactions']) >= 1
        assert all(t['type'] == "payment" for t in data['transactions'])
    
    def test_search_transactions_success(self, client, auth_headers, app):
        """Test successful transaction search"""
        headers = auth_headers()
        
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
        
        response = client.get('/api/transactions/search?q=payment', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'transactions' in data
        assert data['query'] == "payment"
    
    def test_search_transactions_missing_query(self, client, auth_headers):
        """Test transaction search with missing query parameter"""
        headers = auth_headers()
        
        response = client.get('/api/transactions/search', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert "required" in data['message'].lower()
    
    def test_get_transaction_statistics(self, client, auth_headers, app):
        """Test getting transaction statistics"""
        headers = auth_headers()
        
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
        
        response = client.get('/api/transactions/stats', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'statistics' in data
        stats = data['statistics']
        
        assert 'total_transactions' in stats
        assert 'total_amount' in stats
        assert 'by_type' in stats
        assert 'monthly' in stats
    
    def test_all_endpoints_require_auth(self, client):
        """Test that all transaction endpoints require authentication"""
        endpoints = [
            ('GET', '/api/transactions/'),
            ('POST', '/api/transactions/'),
            ('GET', '/api/transactions/1'),
            ('PUT', '/api/transactions/1'),
            ('DELETE', '/api/transactions/1'),
            ('GET', '/api/transactions/by-invoice/1'),
            ('GET', '/api/transactions/by-type/payment'),
            ('GET', '/api/transactions/search?q=test'),
            ('GET', '/api/transactions/stats'),
        ]
        
        for method, endpoint in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, data='{}', content_type='application/json')
            elif method == 'PUT':
                response = client.put(endpoint, data='{}', content_type='application/json')
            elif method == 'DELETE':
                response = client.delete(endpoint)
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require auth"
            data = response.get_json()
            assert data['success'] is False
            assert 'missing' in data['message'].lower() 