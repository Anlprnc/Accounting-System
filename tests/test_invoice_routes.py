import pytest
import json
from datetime import date
from models.customer import Customer
from models.invoice import Invoice
from models import db


class TestInvoiceRoutes:
    
    def test_get_invoices_requires_auth(self, client):
        """Test that getting invoices requires authentication"""
        response = client.get('/api/invoices/')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'missing' in data['message'].lower()
    
    def test_get_invoices_success(self, client, auth_headers, app):
        """Test successful retrieval of invoices"""
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
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
        
        response = client.get('/api/invoices/', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'invoices' in data
        assert 'total' in data
        assert 'pages' in data
    
    def test_get_invoices_pagination(self, client, auth_headers, app):
        """Test invoice pagination"""
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
            
            for i in range(5):
                invoice = Invoice(
                    customer_id=customer.id,
                    date=date(2024, 1, 15),
                    total_amount=1000 + i * 100,
                    status='pending'
                )
                db.session.add(invoice)
            db.session.commit()
        
        response = client.get('/api/invoices/?page=1&per_page=2', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['current_page'] == 1
        assert data['per_page'] == 2
        assert len(data['invoices']) <= 2
    
    def test_get_invoice_by_id_success(self, client, auth_headers, app):
        """Test getting a specific invoice by ID"""
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
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            invoice_id = invoice.id
        
        response = client.get(f'/api/invoices/{invoice_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['invoice']['id'] == invoice_id
        assert data['invoice']['total_amount'] == 1500.50
    
    def test_get_invoice_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent invoice"""
        headers = auth_headers()
        
        response = client.get('/api/invoices/999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'bulunamadı' in data['message']
    
    def test_create_invoice_success(self, client, auth_headers, app):
        """Test successful invoice creation"""
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
            customer_id = customer.id
        
        invoice_data = {
            'customer_id': customer_id,
            'date': '2024-01-15',
            'total_amount': 1500.50,
            'status': 'pending'
        }
        
        response = client.post('/api/invoices/', 
                             headers=headers,
                             data=json.dumps(invoice_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Fatura başarıyla oluşturuldu'
        assert data['invoice']['customer_id'] == customer_id
        assert data['invoice']['total_amount'] == 1500.50
    
    def test_create_invoice_missing_fields(self, client, auth_headers):
        """Test invoice creation with missing required fields"""
        headers = auth_headers()
        
        invoice_data = {
            'customer_id': 1,
        }
        
        response = client.post('/api/invoices/', 
                             headers=headers,
                             data=json.dumps(invoice_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Gerekli alan eksik' in data['message']
    
    def test_create_invoice_invalid_json(self, client, auth_headers):
        """Test invoice creation with invalid JSON"""
        headers = auth_headers()
        
        response = client.post('/api/invoices/', 
                             headers=headers,
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 500
    
    def test_create_invoice_invalid_customer(self, client, auth_headers):
        """Test invoice creation with non-existent customer"""
        headers = auth_headers()
        
        invoice_data = {
            'customer_id': 999,
            'date': '2024-01-15',
            'total_amount': 1500.50,
            'status': 'pending'
        }
        
        response = client.post('/api/invoices/', 
                             headers=headers,
                             data=json.dumps(invoice_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Müşteri bulunamadı' in data['message']
    
    def test_update_invoice_success(self, client, auth_headers, app):
        """Test successful invoice update"""
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
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            invoice_id = invoice.id
        
        update_data = {
            'total_amount': 2000.00,
            'status': 'paid'
        }
        
        response = client.put(f'/api/invoices/{invoice_id}',
                            headers=headers,
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Fatura başarıyla güncellendi'
        assert data['invoice']['total_amount'] == 2000.00
        assert data['invoice']['status'] == 'paid'
    
    def test_update_invoice_not_found(self, client, auth_headers):
        """Test updating non-existent invoice"""
        headers = auth_headers()
        
        update_data = {
            'total_amount': 2000.00
        }
        
        response = client.put('/api/invoices/999',
                            headers=headers,
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Fatura bulunamadı' in data['message']
    
    def test_delete_invoice_admin_only(self, client, auth_headers, admin_headers, app):
        """Test that only admin can delete invoices"""
        user_headers = auth_headers()
        admin_hdrs = admin_headers()
        
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
        
        response = client.delete(f'/api/invoices/{invoice_id}', headers=user_headers)
        assert response.status_code == 403
        
        response = client.delete(f'/api/invoices/{invoice_id}', headers=admin_hdrs)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Fatura başarıyla silindi'
    
    def test_update_invoice_status_success(self, client, auth_headers, app):
        """Test successful invoice status update"""
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
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            invoice_id = invoice.id
        
        status_data = {
            'status': 'paid'
        }
        
        response = client.patch(f'/api/invoices/{invoice_id}/status',
                              headers=headers,
                              data=json.dumps(status_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'paid' in data['message']
        assert data['invoice']['status'] == 'paid'
    
    def test_update_invoice_status_missing_field(self, client, auth_headers, app):
        """Test status update with missing status field"""
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
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            invoice_id = invoice.id
        
        response = client.patch(f'/api/invoices/{invoice_id}/status',
                              headers=headers,
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Status alanı gerekli' in data['message']
    
    def test_get_invoices_by_customer_success(self, client, auth_headers, app):
        """Test getting invoices by customer"""
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
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
            customer_id = customer.id
        
        response = client.get(f'/api/invoices/customer/{customer_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'invoices' in data
        assert 'customer' in data
        assert data['customer']['id'] == customer_id
        assert len(data['invoices']) >= 1
    
    def test_get_invoices_by_customer_not_found(self, client, auth_headers):
        """Test getting invoices by non-existent customer"""
        headers = auth_headers()
        
        response = client.get('/api/invoices/customer/999', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Müşteri bulunamadı' in data['message']
    
    def test_get_invoices_by_status_success(self, client, auth_headers, app):
        """Test getting invoices by status"""
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
            
            statuses = ['pending', 'paid']
            for status in statuses:
                invoice = Invoice(
                    customer_id=customer.id,
                    date=date(2024, 1, 15),
                    total_amount=1500.50,
                    status=status
                )
                db.session.add(invoice)
            db.session.commit()
        
        response = client.get('/api/invoices/status/pending', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['status'] == 'pending'
        assert len(data['invoices']) >= 1
        for invoice in data['invoices']:
            assert invoice['status'] == 'pending'
    
    def test_get_invoices_by_status_invalid(self, client, auth_headers):
        """Test getting invoices by invalid status"""
        headers = auth_headers()
        
        response = client.get('/api/invoices/status/invalid_status', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Geçersiz durum' in data['message']
    
    def test_get_invoice_statistics(self, client, auth_headers, app):
        """Test getting invoice statistics"""
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
            
            statuses = ['pending', 'paid', 'cancelled']
            for status in statuses:
                invoice = Invoice(
                    customer_id=customer.id,
                    date=date(2024, 1, 15),
                    total_amount=1000,
                    status=status
                )
                db.session.add(invoice)
            db.session.commit()
        
        response = client.get('/api/invoices/statistics', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'statistics' in data
        stats = data['statistics']
        
        assert 'total_invoices' in stats
        assert 'pending_invoices' in stats
        assert 'paid_invoices' in stats
        assert 'cancelled_invoices' in stats
        assert 'total_amount' in stats
        assert 'paid_amount' in stats
        assert 'pending_amount' in stats
    
    def test_get_pending_invoices(self, client, auth_headers, app):
        """Test getting pending invoices"""
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
                total_amount=1500.50,
                status='pending'
            )
            db.session.add(invoice)
            db.session.commit()
        
        response = client.get('/api/invoices/pending', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['invoices']) >= 1
        for invoice in data['invoices']:
            assert invoice['status'] == 'pending'
    
    def test_get_paid_invoices(self, client, auth_headers, app):
        """Test getting paid invoices"""
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
                total_amount=1500.50,
                status='paid'
            )
            db.session.add(invoice)
            db.session.commit()
        
        response = client.get('/api/invoices/paid', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        for invoice in data['invoices']:
            assert invoice['status'] == 'paid'
    
    def test_get_overdue_invoices(self, client, auth_headers, app):
        """Test getting overdue invoices"""
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
                total_amount=1500.50,
                status='overdue'
            )
            db.session.add(invoice)
            db.session.commit()
        
        response = client.get('/api/invoices/overdue', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        for invoice in data['invoices']:
            assert invoice['status'] == 'overdue'
    
    def test_all_endpoints_require_authentication(self, client):
        """Test that all endpoints require authentication"""
        endpoints = [
            ('GET', '/api/invoices/'),
            ('GET', '/api/invoices/1'),
            ('POST', '/api/invoices/'),
            ('PUT', '/api/invoices/1'),
            ('PATCH', '/api/invoices/1/status'),
            ('GET', '/api/invoices/customer/1'),
            ('GET', '/api/invoices/status/pending'),
            ('GET', '/api/invoices/statistics'),
            ('GET', '/api/invoices/pending'),
            ('GET', '/api/invoices/paid'),
            ('GET', '/api/invoices/overdue'),
        ]
        
        for method, endpoint in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, json={})
            elif method == 'PUT':
                response = client.put(endpoint, json={})
            elif method == 'PATCH':
                response = client.patch(endpoint, json={})
            
            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False 