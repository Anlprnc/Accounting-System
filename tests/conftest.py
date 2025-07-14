import pytest
import tempfile
import os
from flask import Flask
from models.user import db, User
from models.customer import Customer
from models.invoice import Invoice
from models.transaction import Transaction
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.accounting_routes import accounting_bp
from services.user_service import UserService
from datetime import datetime, date


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    
    db.init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(accounting_bp)
    
    with app.app_context():
        db.create_all()
        
        admin_result = UserService.create_admin_user(
            fullname="Test Admin",
            email="admin@test.com",
            password="admin123"
        )
        
        user_result = UserService.create_user(
            fullname="Test User",
            email="user@test.com", 
            password="user123",
            role="user"
        )
        
        # Create test customers
        customer1 = Customer(
            name="Test Müşteri 1",
            address="Test Adres 1",
            phone="555-0001",
            email="musteri1@test.com"
        )
        customer2 = Customer(
            name="Test Müşteri 2", 
            address="Test Adres 2",
            phone="555-0002",
            email="musteri2@test.com"
        )
        
        db.session.add(customer1)
        db.session.add(customer2)
        db.session.commit()
        
        # Create test invoices
        invoice1 = Invoice(
            customer_id=customer1.id,
            date=date(2024, 1, 15),
            total_amount=1000.0,
            status='paid'
        )
        invoice2 = Invoice(
            customer_id=customer2.id,
            date=date(2024, 1, 20),
            total_amount=2000.0,
            status='pending'
        )
        invoice3 = Invoice(
            customer_id=customer1.id,
            date=date(2024, 2, 10),
            total_amount=1500.0,
            status='paid'
        )
        
        db.session.add(invoice1)
        db.session.add(invoice2)
        db.session.add(invoice3)
        db.session.commit()
        
        # Create test transactions
        transaction1 = Transaction(
            invoice_id=invoice1.id,
            amount=1000.0,
            date=date(2024, 1, 15),
            type='income'
        )
        transaction2 = Transaction(
            invoice_id=invoice3.id,
            amount=1500.0,
            date=date(2024, 2, 10),
            type='income'
        )
        transaction3 = Transaction(
            invoice_id=invoice1.id,
            amount=500.0,
            date=date(2024, 1, 16),
            type='expense'
        )
        transaction4 = Transaction(
            invoice_id=invoice2.id,
            amount=300.0,
            date=date(2024, 1, 25),
            type='expense'
        )
        
        db.session.add(transaction1)
        db.session.add(transaction2)
        db.session.add(transaction3)
        db.session.add(transaction4)
        db.session.commit()
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user_data():
    return {
        'fullname': 'John Doe',
        'email': 'john@test.com',
        'password': 'password123'
    }


@pytest.fixture
def test_admin_data():
    return {
        'fullname': 'Admin User',
        'email': 'admin2@test.com',
        'password': 'admin123'
    }


@pytest.fixture
def auth_headers(client):
    def _get_auth_headers(email="user@test.com", password="user123"):
        response = client.post('/api/auth/login', json={
            'email': email,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.get_json()
            return {'Authorization': f"Bearer {data['token']}"}
        return {}
    
    return _get_auth_headers


@pytest.fixture  
def admin_headers(client):
    def _get_admin_headers():
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        
        if response.status_code == 200:
            data = response.get_json()
            return {'Authorization': f"Bearer {data['token']}"}
        return {}
    
    return _get_admin_headers


@pytest.fixture
def test_customer_data():
    return {
        'name': 'Test Müşteri',
        'address': 'Test Adres',
        'phone': '555-0000',
        'email': 'test@test.com'
    }


@pytest.fixture
def test_invoice_data():
    return {
        'customer_id': 1,
        'date': '2024-01-01',
        'total_amount': 1000.0,
        'status': 'pending'
    }


@pytest.fixture
def test_transaction_data():
    return {
        'invoice_id': 1,
        'amount': 500.0,
        'date': '2024-01-01',
        'type': 'income'
    } 