from models.user import User, db
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any


class UserService:
    
    @staticmethod
    def create_user(fullname: str, email: str, password: str, role: str = 'user') -> Dict[str, Any]:
        """
        Create new user
        
        Args:
            fullname: User's full name
            email: Email address
            password: Password
            role: User role (default: 'user')
            
        Returns:
            Dict: Operation result and user information
        """
        try:
            if UserService.get_user_by_email(email):
                return {
                    'success': False,
                    'message': 'This email address is already in use',
                    'user': None
                }
            
            allowed_roles = ['user', 'admin']
            if role not in allowed_roles:
                role = 'user'
            
            if role == 'admin':
                role = 'user'
            
            user = User(
                fullname=fullname,
                email=email.lower().strip(),
                password=password,
                role=role
            )
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User created successfully',
                'user': user.to_dict()
            }
            
        except IntegrityError:
            db.session.rollback()
            return {
                'success': False,
                'message': 'This email address is already in use',
                'user': None
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating user: {str(e)}',
                'user': None
            }
    
    @staticmethod
    def create_admin_user(fullname: str, email: str, password: str) -> Dict[str, Any]:
        """
        
        Args:
            fullname: User's full name
            email: Email address
            password: Password
            
        Returns:
            Dict: Operation result and user information
        """
        try:
            if UserService.get_user_by_email(email):
                return {
                    'success': False,
                    'message': 'This email address is already in use',
                    'user': None
                }
            
            user = User(
                fullname=fullname,
                email=email.lower().strip(),
                password=password,
                role='admin'
            )
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Admin user created successfully',
                'user': user.to_dict()
            }
            
        except IntegrityError:
            db.session.rollback()
            return {
                'success': False,
                'message': 'This email address is already in use',
                'user': None
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating admin user: {str(e)}',
                'user': None
            }
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return db.session.get(User, user_id)
        except Exception:
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return User.query.filter_by(email=email.lower().strip()).first()
        except Exception:
            return None
    
    @staticmethod
    def get_all_users(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get all users paginated
        
        Args:
            page: Page
        """
        try:
            users = User.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'users': [user.to_dict() for user in users.items],
                'total': users.total,
                'pages': users.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting users: {str(e)}',
                'users': []
            }
    
    @staticmethod
    def get_users_by_role(role: str) -> List[User]:
        """Get users by role"""
        try:
            return User.query.filter_by(role=role).all()
        except Exception:
            return []
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Dict: Operation result
        """
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found',
                    'user': None
                }
            
            for key, value in kwargs.items():
                if hasattr(user, key) and key != 'id':
                    if key == 'password':
                        user.set_password(value)
                    elif key == 'email':
                        existing_user = UserService.get_user_by_email(value)
                        if existing_user and existing_user.id != user_id:
                            return {
                                'success': False,
                                'message': 'This email address is already in use',
                                'user': None
                            }
                        setattr(user, key, value.lower().strip())
                    elif key == 'role':
                        allowed_roles = ['user', 'admin']
                        if value in allowed_roles:
                            setattr(user, key, value)
                    else:
                        setattr(user, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User updated successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating user: {str(e)}',
                'user': None
            }
    
    @staticmethod
    def delete_user(user_id: int) -> Dict[str, Any]:
        """
        Delete user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: Operation result
        """
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            db.session.delete(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting user: {str(e)}'
            }
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Dict[str, Any]:
        """
        User authentication
        
        Args:
            email: Email address
            password: Password
            
        Returns:
            Dict: Authentication result
        """
        try:
            user = UserService.get_user_by_email(email)
            
            if not user:
                return {
                    'success': False,
                    'message': 'Email or password is incorrect',
                    'user': None
                }
            
            if not user.check_password(password):
                return {
                    'success': False,
                    'message': 'Email or password is incorrect',
                    'user': None
                }
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error authenticating user: {str(e)}',
                'user': None
            }
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Dict: Operation result
        """
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            if not user.check_password(current_password):
                return {
                    'success': False,
                    'message': 'Current password is incorrect'
                }
            
            user.set_password(new_password)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error changing password: {str(e)}'
            }
    
    @staticmethod
    def search_users(query: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Search users by name or email
        
        Args:
            query: Search query
            page: Page number
            per_page: Users per page
            
        Returns:
            Dict: Search results
        """
        try:
            search_pattern = f"%{query.lower()}%"
            users = User.query.filter(
                db.or_(
                    User.fullname.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'success': True,
                'users': [user.to_dict() for user in users.items],
                'total': users.total,
                'pages': users.pages,
                'current_page': page,
                'per_page': per_page,
                'query': query
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error searching users: {str(e)}',
                'users': []
            }
