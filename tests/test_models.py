import pytest
from models.user import User, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    def test_user_creation(self, app):
        with app.app_context():
            user = User(
                fullname="Test User",
                email="test@example.com",
                password="password123",
                role="user"
            )
            
            assert user.fullname == "Test User"
            assert user.email == "test@example.com"
            assert user.role == "user"
            assert user.password != "password123"
            assert user.id is None
    
    def test_password_hashing(self, app):
        with app.app_context():
            user = User(
                fullname="Test User",
                email="test@example.com",
                password="password123"
            )
            
            assert user.password != "password123"
            assert len(user.password) > 50
    
    def test_password_verification(self, app):
        with app.app_context():
            user = User(
                fullname="Test User",
                email="test@example.com",
                password="password123"
            )
            
            assert user.check_password("password123") is True
            
            assert user.check_password("wrongpassword") is False
    
    def test_set_password_method(self, app):
        with app.app_context():
            user = User(
                fullname="Test User",
                email="test@example.com",
                password="oldpassword"
            )
            
            old_hash = user.password
            user.set_password("newpassword")
            
            assert user.password != old_hash
            assert user.check_password("newpassword") is True
            assert user.check_password("oldpassword") is False
    
    def test_default_values(self, app):
        with app.app_context():
            user = User(
                fullname="Test User",
                email="test@example.com",
                password="password123"
            )
            
            assert user.role == "user"
    
    def test_to_dict_method(self, app):
        with app.app_context():
            user = User(
                fullname="Test User",
                email="test@example.com",
                password="password123",
                role="admin"
            )
            
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            assert user_dict['id'] == user.id
            assert user_dict['fullname'] == "Test User"
            assert user_dict['email'] == "test@example.com"
            assert user_dict['role'] == "admin"
            
            assert 'password' not in user_dict
            
            assert 'created_at' in user_dict
            assert 'updated_at' in user_dict
    
    def test_repr_method(self, app):
        with app.app_context():
            user = User(
                fullname="Test User",
                email="test@example.com",
                password="password123"
            )
            
            repr_str = repr(user)
            assert "test@example.com" in repr_str
            assert "User" in repr_str
    
    def test_email_case_insensitive(self, app):
        with app.app_context():
            user1 = User(
                fullname="User 1",
                email="TEST@EXAMPLE.COM",
                password="password123"
            )
            
            assert user1.email == "test@example.com"
            
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(
                fullname="User 2", 
                email="Test@Example.Com",
                password="password123"
            )
            
            assert user2.email == "test@example.com"
            
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            
            db.session.rollback()
    
    def test_user_persistence(self, app):
        with app.app_context():
            user = User(
                fullname="Persistent User",
                email="persistent@example.com",
                password="password123",
                role="admin"
            )
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            
            retrieved_user = User.query.filter_by(email="persistent@example.com").first()
            
            assert retrieved_user is not None
            assert retrieved_user.fullname == "Persistent User"
            assert retrieved_user.role == "admin"
            assert retrieved_user.check_password("password123") is True
    
    def test_user_timestamps(self, app):
        with app.app_context():
            user = User(
                fullname="Timestamp User",
                email="timestamp@example.com",
                password="password123"
            )
            
            db.session.add(user)
            db.session.commit()
            
            assert user.created_at is not None
            assert user.updated_at is not None
            assert isinstance(user.created_at, datetime)
            assert isinstance(user.updated_at, datetime)
            
            now = datetime.now()
            time_diff = now - user.created_at
            assert time_diff.total_seconds() < 10