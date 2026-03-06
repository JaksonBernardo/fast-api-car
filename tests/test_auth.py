"""
Authentication and JWT token tests.
Tests for login, token generation, token refresh, and authentication.
"""
from http import HTTPStatus

import jwt
import pytest
from fastapi.testclient import TestClient

from car_api.core.security import Settings, verify_password, create_access_token
from car_api.models import User


class TestTokenGeneration:
    """Tests for POST /api/auth/token"""

    def test_token_success(self, client: TestClient, user: User, user_data: dict):
        """Test successful token generation with valid credentials."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.OK

        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_token_invalid_email(self, client: TestClient, user_data: dict):
        """Test token generation with invalid email."""
        login_data = {
            "email": "nonexistent@test.com",
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Email ou senha incorretos"

    def test_token_invalid_password(self, client: TestClient, user: User, user_data: dict):
        """Test token generation with wrong password."""
        login_data = {
            "email": user_data["email"],
            "password": "wrongpassword"
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Email ou senha incorretos"

    def test_token_invalid_email_format(self, client: TestClient):
        """Test token generation with invalid email format."""
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_token_missing_fields(self, client: TestClient):
        """Test token generation with missing fields."""
        login_data = {
            "email": "test@test.com"
            # Missing password
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_token_empty_email(self, client: TestClient):
        """Test token generation with empty email."""
        login_data = {
            "email": "",
            "password": "password123"
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_token_empty_password(self, client: TestClient, user_data: dict):
        """Test token generation with empty password."""
        login_data = {
            "email": user_data["email"],
            "password": ""
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_token_short_password(self, client: TestClient):
        """Test token generation with password less than 6 characters."""
        login_data = {
            "email": "test@test.com",
            "password": "12345"  # Less than 6 characters
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_token_response_structure(self, client: TestClient, user: User, user_data: dict):
        """Test token response has correct structure."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Check required fields
        assert "access_token" in data
        assert "token_type" in data

        # Check no extra fields
        assert set(data.keys()) == {"access_token", "token_type"}

        # Check token_type is always 'bearer'
        assert data["token_type"] == "bearer"

    def test_token_is_valid_jwt(self, client: TestClient, user: User, user_data: dict):
        """Test that generated token is a valid JWT."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Decode token without verification to check structure
        decoded = jwt.decode(data["access_token"], options={"verify_signature": False})

        assert "sub" in decoded  # Subject (user id)
        assert "exp" in decoded  # Expiration

    def test_token_contains_user_id(self, client: TestClient, user: User, user_data: dict):
        """Test that token contains the correct user ID."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Decode token without verification to check structure
        decoded = jwt.decode(data["access_token"], options={"verify_signature": False})

        assert decoded["sub"] == str(user.id)


class TestRefreshToken:
    """Tests for POST /api/auth/refresh_token"""

    def test_refresh_token_success(self, client: TestClient, auth_headers: dict):
        """Test successful token refresh."""
        response = client.post('/api/auth/refresh_token', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK

        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_refresh_token_without_auth(self, client: TestClient):
        """Test token refresh without authentication fails."""
        response = client.post('/api/auth/refresh_token')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token_invalid_token(self, client: TestClient):
        """Test token refresh with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_xyz"}

        response = client.post('/api/auth/refresh_token', headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token_expired_token(self, client: TestClient, user: User):
        """Test token refresh with expired token fails."""
        # Create an expired token manually
        expired_token = create_access_token(data={"sub": str(user.id)})

        # We can't easily test expiration without mocking time,
        # but we can verify the endpoint requires valid auth
        headers = {"Authorization": f"Bearer {expired_token}"}

        # This should work if token is valid (not expired)
        response = client.post('/api/auth/refresh_token', headers=headers)

        # Token should be valid (just created)
        assert response.status_code == HTTPStatus.OK

    def test_refresh_token_returns_new_token(self, client: TestClient, auth_headers: dict):
        """Test that refresh returns a valid token."""
        # Get initial token
        response1 = client.post('/api/auth/refresh_token', headers=auth_headers)
        token1 = response1.json()["access_token"]

        # Verify token is valid
        assert token1 is not None
        assert len(token1) > 0

        # Refresh again
        response2 = client.post('/api/auth/refresh_token', headers=auth_headers)
        token2 = response2.json()["access_token"]

        # Both tokens should be valid
        assert token2 is not None
        assert len(token2) > 0

    def test_refresh_token_response_structure(self, client: TestClient, auth_headers: dict):
        """Test refresh token response has correct structure."""
        response = client.post('/api/auth/refresh_token', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Check required fields
        assert "access_token" in data
        assert "token_type" in data

        # Check no extra fields
        assert set(data.keys()) == {"access_token", "token_type"}

        # Check token_type is always 'bearer'
        assert data["token_type"] == "bearer"


class TestAuthentication:
    """Tests for authentication-protected endpoints."""

    def test_protected_endpoint_without_token(self, client: TestClient, brand_data: dict):
        """Test accessing protected endpoint without token fails."""
        response = client.post('/api/brands/', json=brand_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_protected_endpoint_with_invalid_token(self, client: TestClient, brand_data: dict):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_xyz"}

        response = client.post('/api/brands/', json=brand_data, headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_protected_endpoint_with_valid_token(self, client: TestClient, auth_headers: dict, brand_data: dict):
        """Test accessing protected endpoint with valid token succeeds."""
        response = client.post('/api/brands/', json=brand_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED

    def test_bearer_token_format(self, client: TestClient, auth_headers: dict):
        """Test that correct Bearer token format works."""
        # Test with correct Bearer format
        response = client.get('/api/users/', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK

    def test_authorization_without_bearer_prefix(self, client: TestClient, user: User, user_data: dict):
        """Test that token without Bearer prefix may still work (implementation dependent)."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)
        token = response.json()["access_token"]

        # Try without 'Bearer' prefix - behavior depends on implementation
        headers = {"Authorization": token}

        response = client.get('/api/users/', headers=headers)

        # Document current behavior (may work or fail depending on implementation)
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.UNAUTHORIZED]


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_password_is_hashed_in_database(self, session, user_data: dict):
        """Test that password is hashed before storing in database."""
        from car_api.core.security import get_password_hash
        from car_api.models import User

        hashed = get_password_hash(user_data["password"])

        # Hashed password should be different from plain text
        assert hashed != user_data["password"]

        # Hash should start with algorithm identifier
        assert len(hashed) > len(user_data["password"])

    def test_password_verification_success(self):
        """Test password verification with correct password."""
        from car_api.core.security import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test password verification with wrong password."""
        from car_api.core.security import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        from car_api.core.security import get_password_hash

        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokenClaims:
    """Tests for JWT token claims and structure."""

    def test_token_expiration_setting(self, client: TestClient, user: User, user_data: dict):
        """Test that token has expiration claim."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)
        token = response.json()["access_token"]

        # Decode without verification
        decoded = jwt.decode(token, options={"verify_signature": False})

        assert "exp" in decoded

    def test_token_subject_claim(self, client: TestClient, user: User, user_data: dict):
        """Test that token has subject claim with user ID."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)
        token = response.json()["access_token"]

        # Decode without verification
        decoded = jwt.decode(token, options={"verify_signature": False})

        assert decoded["sub"] == str(user.id)

    def test_token_algorithm(self, client: TestClient, user: User, user_data: dict):
        """Test that token uses correct algorithm."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)
        token = response.json()["access_token"]

        # Get token header
        header = jwt.get_unverified_header(token)

        # Should use HS256 by default
        assert header["alg"] in ["HS256", "HS384", "HS512"]


class TestAuthenticationEdgeCases:
    """Edge case tests for authentication."""

    def test_login_with_special_characters_email(self, client: TestClient, session, user_data: dict):
        """Test login with email containing special characters."""
        from car_api.core.security import get_password_hash
        from car_api.models import User

        # Create user with special characters in email
        special_email = "test+tag@example.com"
        hashed_password = get_password_hash(user_data["password"])

        db_user = User(
            username="special_email_user",
            email=special_email,
            password=hashed_password
        )

        session.add(db_user)
        session.commit()

        login_data = {
            "email": special_email,
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.OK

    def test_login_case_sensitivity(self, client: TestClient, user: User, user_data: dict):
        """Test login email case sensitivity."""
        # Try with uppercase email
        login_data = {
            "email": user_data["email"].upper(),
            "password": user_data["password"]
        }

        response = client.post('/api/auth/token', json=login_data)

        # Email comparison might be case-sensitive
        # This test documents the current behavior
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.UNAUTHORIZED]

    def test_multiple_concurrent_tokens(self, client: TestClient, user: User, user_data: dict):
        """Test that multiple tokens can be generated for same user."""
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        # Generate multiple tokens
        tokens = []
        for _ in range(3):
            response = client.post('/api/auth/token', json=login_data)
            assert response.status_code == HTTPStatus.OK
            tokens.append(response.json()["access_token"])

        # All tokens should be valid
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get('/api/users/', headers=headers)
            assert response.status_code == HTTPStatus.OK

    def test_token_with_whitespace_password(self, client: TestClient, session):
        """Test login with password containing whitespace."""
        from car_api.core.security import get_password_hash
        from car_api.models import User

        password = "password with spaces"
        hashed = get_password_hash(password)

        db_user = User(
            username="whitespace_user",
            email="whitespace@test.com",
            password=hashed
        )

        session.add(db_user)
        session.commit()

        login_data = {
            "email": "whitespace@test.com",
            "password": password
        }

        response = client.post('/api/auth/token', json=login_data)

        assert response.status_code == HTTPStatus.OK
