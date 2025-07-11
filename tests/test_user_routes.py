import pytest
import json


class TestUserRoutes:
    def test_get_users_admin_access(self, client, admin_headers):
        headers = admin_headers()
        
        response = client.get('/api/users/', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'users' in data
        assert 'total' in data
        assert 'pages' in data
        assert len(data['users']) >= 2
    
    def test_get_users_user_access_denied(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.get('/api/users/', headers=headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'admin' in data['message'].lower()
    
    def test_get_users_no_token(self, client):
        response = client.get('/api/users/')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'missing' in data['message'].lower()
    
    def test_get_users_pagination(self, client, admin_headers):
        headers = admin_headers()
        
        response = client.get('/api/users/?page=1&per_page=1', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['current_page'] == 1
        assert data['per_page'] == 1
        assert len(data['users']) == 1
    
    def test_get_user_self_access(self, client, auth_headers):
        headers = auth_headers()
        
        profile_response = client.get('/api/users/me', headers=headers)
        user_id = profile_response.get_json()['user']['id']
        
        response = client.get(f'/api/users/{user_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['email'] == 'user@test.com'
    
    def test_get_user_other_user_denied(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.get('/api/users/1', headers=headers)
        
        if response.status_code == 403:
            data = response.get_json()
            assert data['success'] is False
            assert 'access denied' in data['message'].lower()
    
    def test_get_user_admin_can_access_any(self, client, admin_headers):
        headers = admin_headers()
        
        users_response = client.get('/api/users/', headers=headers)
        users = users_response.get_json()['users']
        user_id = users[0]['id']
        
        response = client.get(f'/api/users/{user_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_get_user_not_found(self, client, admin_headers):
        headers = admin_headers()
        
        response = client.get('/api/users/99999', headers=headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['message'].lower()
    
    def test_update_user_self(self, client, auth_headers):
        headers = auth_headers()
        
        profile_response = client.get('/api/users/me', headers=headers)
        user_id = profile_response.get_json()['user']['id']
        
        response = client.put(f'/api/users/{user_id}', 
            headers=headers,
            json={
                'fullname': 'Updated Name',
                'email': 'updated@test.com'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['fullname'] == 'Updated Name'
        assert data['user']['email'] == 'updated@test.com'
    
    def test_update_user_role_restriction(self, client, auth_headers):
        headers = auth_headers()
        
        profile_response = client.get('/api/users/me', headers=headers)
        user_id = profile_response.get_json()['user']['id']
        
        response = client.put(f'/api/users/{user_id}',
            headers=headers,
            json={
                'fullname': 'Updated Name',
                'role': 'admin'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'user'
    
    def test_update_user_other_user_denied(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.put('/api/users/1',
            headers=headers,
            json={'fullname': 'Hacked Admin'}
        )
        
        if response.status_code == 403:
            data = response.get_json()
            assert data['success'] is False
            assert 'access denied' in data['message'].lower()
    
    def test_update_user_admin_can_update_any(self, client, admin_headers):
        headers = admin_headers()
        
        register_response = client.post('/api/auth/register', json={
            'fullname': 'Update Test User',
            'email': 'updatetest@test.com',
            'password': 'password123'
        })
        user_data = register_response.get_json()['user']
        
        response = client.put(f'/api/users/{user_data["id"]}',
            headers=headers,
            json={
                'fullname': 'Admin Updated Name',
                'role': 'admin'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['fullname'] == 'Admin Updated Name'
        assert data['user']['role'] == 'admin'
    
    def test_delete_user_admin_only(self, client, admin_headers, auth_headers):
        register_response = client.post('/api/auth/register', json={
            'fullname': 'Delete Test User',
            'email': 'deletetest@test.com',
            'password': 'password123'
        })
        user_id = register_response.get_json()['user']['id']
        
        user_headers = auth_headers()
        response = client.delete(f'/api/users/{user_id}', headers=user_headers)
        assert response.status_code == 403
        
        admin_headers_obj = admin_headers()
        response = client.delete(f'/api/users/{user_id}', headers=admin_headers_obj)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'deleted' in data['message'].lower()
    
    def test_search_users_admin_only(self, client, admin_headers, auth_headers):
        user_headers = auth_headers()
        response = client.get('/api/users/search?q=test', headers=user_headers)
        assert response.status_code == 403
        
        admin_headers_obj = admin_headers()
        response = client.get('/api/users/search?q=test', headers=admin_headers_obj)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
    
    def test_search_users_missing_query(self, client, admin_headers):
        headers = admin_headers()
        
        response = client.get('/api/users/search', headers=headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'required' in data['message'].lower()
    
    def test_get_users_by_role_admin_only(self, client, admin_headers, auth_headers):
        user_headers = auth_headers()
        response = client.get('/api/users/by-role/user', headers=user_headers)
        assert response.status_code == 403
        
        admin_headers_obj = admin_headers()
        response = client.get('/api/users/by-role/user', headers=admin_headers_obj)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
        assert data['role'] == 'user'
    
    def test_get_user_by_email_admin_only(self, client, admin_headers, auth_headers):
        user_headers = auth_headers()
        response = client.get('/api/users/by-email/user@test.com', headers=user_headers)
        assert response.status_code == 403
        
        admin_headers_obj = admin_headers()
        response = client.get('/api/users/by-email/user@test.com', headers=admin_headers_obj)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['email'] == 'user@test.com'
    
    def test_get_user_stats_admin_only(self, client, admin_headers, auth_headers):
        user_headers = auth_headers()
        response = client.get('/api/users/stats', headers=user_headers)
        assert response.status_code == 403
        
        admin_headers_obj = admin_headers()
        response = client.get('/api/users/stats', headers=admin_headers_obj)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'stats' in data
        assert 'total_users' in data['stats']
        assert 'admin_users' in data['stats']
        assert 'regular_users' in data['stats']
    
    def test_get_current_user_me(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.get('/api/users/me', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['email'] == 'user@test.com'
        assert 'password' not in data['user']
    
    def test_update_current_user_me(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.put('/api/users/me',
            headers=headers,
            json={
                'fullname': 'Updated via ME',
                'email': 'newme@test.com',
                'role': 'admin'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['fullname'] == 'Updated via ME'
        assert data['user']['email'] == 'newme@test.com'
        assert data['user']['role'] == 'user'
    
    def test_update_current_user_no_data(self, client, auth_headers):
        headers = auth_headers()
        
        response = client.put('/api/users/me', headers=headers, json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'not provided' in data['message'].lower()
    
    def test_me_endpoints_require_token(self, client):
        response = client.get('/api/users/me')
        assert response.status_code == 401
        
        response = client.put('/api/users/me', json={'fullname': 'Test'})
        assert response.status_code == 401
    
    def test_user_cannot_access_admin_endpoints(self, client, auth_headers):
        headers = auth_headers()
        
        admin_endpoints = [
            ('GET', '/api/users/'),
            ('GET', '/api/users/search?q=test'),
            ('GET', '/api/users/by-role/user'),
            ('GET', '/api/users/by-email/test@test.com'),
            ('GET', '/api/users/stats'),
            ('DELETE', '/api/users/1')
        ]
        
        for method, endpoint in admin_endpoints:
            if method == 'GET':
                response = client.get(endpoint, headers=headers)
            elif method == 'DELETE':
                response = client.delete(endpoint, headers=headers)
            
            assert response.status_code == 403
            data = response.get_json()
            assert data['success'] is False
    
    def test_duplicate_email_update_prevention(self, client, auth_headers):
        client.post('/api/auth/register', json={
            'fullname': 'User One',
            'email': 'user1@duplicate.com',
            'password': 'password123'
        })
        
        register_response = client.post('/api/auth/register', json={
            'fullname': 'User Two',
            'email': 'user2@duplicate.com',
            'password': 'password123'
        })
        
        user2_id = register_response.get_json()['user']['id']
        
        login_response = client.post('/api/auth/login', json={
            'email': 'user2@duplicate.com',
            'password': 'password123'
        })
        user2_token = login_response.get_json()['token']
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        
        response = client.put(f'/api/users/{user2_id}',
            headers=user2_headers,
            json={'email': 'user1@duplicate.com'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'already in use' in data['message'] 