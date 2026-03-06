"""
User CRUD operation tests.
Tests for user creation, reading, updating, and deletion via API endpoints.
"""
from http import HTTPStatus
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from car_api.models import User


class TestCreateUser:
    """Tests for POST /api/users/"""

    def test_create_user_success(self, client: TestClient, user_data: dict):
        """Test creating a new user successfully."""
        response = client.post('/api/users/', json=user_data)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()

        assert data['username'] == user_data['username']
        assert data['email'] == user_data['email']
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'password' not in data  # Password should not be returned

    def test_create_user_duplicate_email(self, client: TestClient, user: User, user_data: dict):
        """Test creating a user with duplicate email fails."""
        # Try to create user with same email as existing user
        duplicate_user = {
            'username': 'different_user',
            'email': user.email,  # Same email
            'password': 'password123'
        }

        response = client.post('/api/users/', json=duplicate_user)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.json()
        assert 'detail' in data

    def test_create_user_duplicate_username(self, client: TestClient, user: User, user_data: dict):
        """Test creating a user with duplicate username fails."""
        # Try to create user with same username as existing user
        duplicate_user = {
            'username': user.username,  # Same username
            'email': 'different@test.com',
            'password': 'password123'
        }

        response = client.post('/api/users/', json=duplicate_user)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.json()
        assert 'detail' in data

    def test_create_user_invalid_email(self, client: TestClient):
        """Test creating a user with invalid email fails."""
        invalid_user = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123'
        }

        response = client.post('/api/users/', json=invalid_user)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_short_username(self, client: TestClient):
        """Test creating a user with username less than 3 characters fails."""
        invalid_user = {
            'username': 'ab',  # Less than 3 characters
            'email': 'valid@test.com',
            'password': 'password123'
        }

        response = client.post('/api/users/', json=invalid_user)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_short_password(self, client: TestClient):
        """Test creating a user with password less than 6 characters fails."""
        invalid_user = {
            'username': 'testuser',
            'email': 'valid@test.com',
            'password': '12345'  # Less than 6 characters
        }

        response = client.post('/api/users/', json=invalid_user)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_missing_fields(self, client: TestClient):
        """Test creating a user with missing required fields fails."""
        # Missing email
        invalid_user = {
            'username': 'testuser',
            'password': 'password123'
        }

        response = client.post('/api/users/', json=invalid_user)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_empty_username(self, client: TestClient):
        """Test creating a user with empty username fails."""
        invalid_user = {
            'username': '',
            'email': 'valid@test.com',
            'password': 'password123'
        }

        response = client.post('/api/users/', json=invalid_user)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestGetUserById:
    """Tests for GET /api/users/{user_id}"""

    def test_get_user_by_id_success(self, client: TestClient, user: User):
        """Test getting a user by ID successfully."""
        response = client.get(f'/api/users/{user.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email
        assert 'password' not in data

    def test_get_user_by_id_not_found(self, client: TestClient):
        """Test getting a non-existent user returns 404."""
        response = client.get('/api/users/99999')

        assert response.status_code == HTTPStatus.NOT_FOUND
        data = response.json()
        assert data['detail'] == 'Usuário não encontrado'

    def test_get_user_by_id_invalid_id(self, client: TestClient):
        """Test getting a user with invalid ID format fails."""
        response = client.get('/api/users/invalid')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestListUsers:
    """Tests for GET /api/users/"""

    def test_list_users_success(self, client: TestClient, user: User, second_user: User):
        """Test listing users successfully."""
        response = client.get('/api/users/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert 'users' in data
        assert 'offset' in data
        assert 'limit' in data
        assert len(data['users']) >= 2

    def test_list_users_with_pagination(self, client: TestClient, user: User, second_user: User):
        """Test listing users with pagination."""
        response = client.get('/api/users/?offset=0&limit=1')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['users']) == 1
        assert data['offset'] == 0
        assert data['limit'] == 1

    def test_list_users_with_search_username(self, client: TestClient, user: User, second_user: User):
        """Test listing users with search by username."""
        response = client.get(f'/api/users/?search={user.username}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['users']) >= 1
        assert data['users'][0]['username'] == user.username

    def test_list_users_with_search_email(self, client: TestClient, user: User):
        """Test listing users with search by email."""
        response = client.get(f'/api/users/?search={user.email}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['users']) >= 1
        assert data['users'][0]['email'] == user.email

    def test_list_users_with_search_no_results(self, client: TestClient):
        """Test listing users with search that returns no results."""
        response = client.get('/api/users/?search=nonexistent_user_xyz')

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert len(data['users']) == 0

    def test_list_users_invalid_limit(self, client: TestClient):
        """Test listing users with invalid limit fails."""
        response = client.get('/api/users/?limit=0')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_list_users_invalid_offset(self, client: TestClient):
        """Test listing users with negative offset fails."""
        response = client.get('/api/users/?offset=-1')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_list_users_limit_exceeds_max(self, client: TestClient):
        """Test listing users with limit exceeding maximum fails."""
        response = client.get('/api/users/?limit=101')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestUpdateUser:
    """Tests for PUT /api/users/{user_id}"""

    def test_update_user_success(self, client: TestClient, user: User, auth_headers: dict):
        """Test updating a user successfully."""
        update_data = {
            'username': 'updated_username',
            'email': 'updated@test.com'
        }

        response = client.put(f'/api/users/{user.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['username'] == 'updated_username'
        assert data['email'] == 'updated@test.com'

    def test_update_user_unauthorized(self, client: TestClient, user: User, second_user: User, user_data: dict):
        """Test updating another user's data without permission fails."""
        update_data = {
            'username': 'hacked_username'
        }

        # Login as second_user and try to update user
        login_response = client.post('/api/auth/token', json={
            'email': second_user.email if hasattr(second_user, 'email') else 'second@test.com',
            'password': 'password456'
        })

        if login_response.status_code == HTTPStatus.OK:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}

            response = client.put(f'/api/users/{user.id}', json=update_data, headers=headers)

            assert response.status_code == HTTPStatus.FORBIDDEN

    def test_update_user_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating a non-existent user returns 404."""
        update_data = {
            'username': 'updated_username'
        }

        response = client.put('/api/users/99999', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_user_duplicate_email(self, client: TestClient, user: User, second_user: User, auth_headers: dict):
        """Test updating user with another user's email fails."""
        update_data = {
            'email': second_user.email  # Use second user's email
        }

        response = client.put(f'/api/users/{user.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_update_user_short_username(self, client: TestClient, user: User, auth_headers: dict):
        """Test updating user with short username fails."""
        update_data = {
            'username': 'ab'  # Less than 3 characters
        }

        response = client.put(f'/api/users/{user.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_update_user_short_password(self, client: TestClient, user: User, auth_headers: dict):
        """Test updating user with short password fails."""
        update_data = {
            'password': '12345'  # Less than 6 characters
        }

        response = client.put(f'/api/users/{user.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_update_user_password(self, client: TestClient, user: User, auth_headers: dict):
        """Test updating user password."""
        update_data = {
            'password': 'newpassword123'
        }

        response = client.put(f'/api/users/{user.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK

        # Verify new password works
        login_response = client.post('/api/auth/token', json={
            'email': user.email,
            'password': 'newpassword123'
        })

        assert login_response.status_code == HTTPStatus.OK

    def test_update_user_partial_update(self, client: TestClient, user: User, auth_headers: dict):
        """Test partial update of user."""
        update_data = {
            'username': 'partial_update'
        }

        response = client.put(f'/api/users/{user.id}', json=update_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        assert data['username'] == 'partial_update'
        assert data['email'] == user.email  # Email should remain unchanged


class TestDeleteUser:
    """Tests for DELETE /api/users/{user_id}"""

    def test_delete_user_success(self, client: TestClient, user: User, auth_headers: dict):
        """Test deleting a user successfully."""
        response = client.delete(f'/api/users/{user.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verify user is deleted
        get_response = client.get(f'/api/users/{user.id}')
        assert get_response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_user_unauthorized(self, client: TestClient, user: User, second_user: User):
        """Test deleting another user's account without permission fails."""
        # Login as second_user
        login_response = client.post('/api/auth/token', json={
            'email': 'second@test.com',
            'password': 'password456'
        })

        if login_response.status_code == HTTPStatus.OK:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}

            response = client.delete(f'/api/users/{user.id}', headers=headers)

            assert response.status_code == HTTPStatus.FORBIDDEN

    def test_delete_user_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting a non-existent user returns 404."""
        response = client.delete('/api/users/99999', headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_user_without_auth(self, client: TestClient, user: User):
        """Test deleting a user without authentication fails."""
        response = client.delete(f'/api/users/{user.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestUserSchemaValidation:
    """Tests for user schema validation."""

    def test_user_schema_email_format(self, client: TestClient, auth_headers: dict):
        """Test user creation with various email formats."""
        valid_emails = [
            'test1@example.com',
            'user.name@domain.org',
            'user+tag@example.co.uk'
        ]

        for email in valid_emails:
            user_data = {
                'username': f'testuser_{email.replace("@", "_").replace(".", "_")}',
                'email': email,
                'password': 'password123'
            }

            response = client.post('/api/users/', json=user_data, headers=auth_headers)

            assert response.status_code == HTTPStatus.CREATED, f"Failed for email: {email}"

    def test_user_schema_special_characters_username(self, client: TestClient):
        """Test user creation with special characters in username."""
        user_data = {
            'username': 'test_user-123',
            'email': 'special@test.com',
            'password': 'password123'
        }

        response = client.post('/api/users/', json=user_data)

        assert response.status_code == HTTPStatus.CREATED

    def test_user_schema_long_username(self, client: TestClient):
        """Test user creation with long username."""
        user_data = {
            'username': 'a' * 100,  # 100 characters
            'email': 'long@test.com',
            'password': 'password123'
        }

        response = client.post('/api/users/', json=user_data)

        assert response.status_code == HTTPStatus.CREATED
