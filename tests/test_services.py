import pytest
from services.user_service import UserService
from models.user import User, db


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