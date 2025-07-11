import pytest
import tempfile
import os
from flask import Flask
from models.user import db, User
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from services.user_service import UserService


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