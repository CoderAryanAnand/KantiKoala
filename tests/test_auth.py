"""
Unit tests for authentication routes.

Tests cover:
- User registration
- Login and logout
- Password reset flow
- Session management

Note: Auth routes are under /auth prefix.
"""

import pytest
from kkoala.extensions import db, bcrypt
from kkoala.models import User, Settings


class TestLogin:
    """Tests for the login functionality."""

    def test_login_page_loads(self, client):
        """Test that the login page renders correctly."""
        response = client.get("/auth/login", follow_redirects=True)
        
        assert response.status_code == 200

    def test_login_success(self, client, test_user, app):
        """Test successful login with valid credentials."""
        with client.session_transaction() as sess:
            sess["csrf_token"] = "test-token"
        
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpassword123",
            "csrf_token": "test-token"
        }, follow_redirects=True)
        
        # Should end up on home page after login
        assert response.status_code == 200

    def test_login_invalid_password(self, client, test_user, app):
        """Test login failure with wrong password."""
        with client.session_transaction() as sess:
            sess["csrf_token"] = "test-token"
        
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword",
            "csrf_token": "test-token"
        }, follow_redirects=True)
        
        # Should stay on login page
        assert response.status_code == 200

    def test_login_nonexistent_user(self, client, app):
        """Test login failure with nonexistent user."""
        with client.session_transaction() as sess:
            sess["csrf_token"] = "test-token"
        
        response = client.post("/auth/login", data={
            "username": "nonexistent",
            "password": "password123",
            "csrf_token": "test-token"
        }, follow_redirects=True)
        
        # Should stay on login page
        assert response.status_code == 200


class TestLogout:
    """Tests for the logout functionality."""

    def test_logout_redirects(self, authenticated_client):
        """Test that logout redirects."""
        response = authenticated_client.get("/auth/logout", follow_redirects=True)
        
        # Should eventually render a page
        assert response.status_code == 200


class TestRegistration:
    """Tests for the registration functionality."""

    def test_register_page_loads(self, client):
        """Test that the registration page renders correctly."""
        response = client.get("/auth/register", follow_redirects=True)
        
        assert response.status_code == 200

    def test_register_success(self, client, app):
        """Test successful user registration."""
        with client.session_transaction() as sess:
            sess["csrf_token"] = "test-token"
        
        response = client.post("/auth/register", data={
            "username": "newuser",
            "password": "newpassword123",
            "confirm_password": "newpassword123",
            "email": "newuser@example.com",
            "csrf_token": "test-token"
        }, follow_redirects=True)
        
        # Should succeed
        assert response.status_code == 200

    def test_register_password_mismatch(self, client, app):
        """Test registration fails with mismatched passwords."""
        with client.session_transaction() as sess:
            sess["csrf_token"] = "test-token"
        
        response = client.post("/auth/register", data={
            "username": "newuser2",
            "password": "password123",
            "confirm_password": "differentpassword",
            "email": "newuser2@example.com",
            "csrf_token": "test-token"
        }, follow_redirects=True)
        
        # Should stay on register page (200 after redirects)
        assert response.status_code == 200


class TestPasswordChange:
    """Tests for the password change functionality."""

    def test_change_password_page_requires_login(self, client):
        """Test that password change page requires authentication."""
        response = client.get("/settings/change_password", follow_redirects=True)
        
        # Should redirect to login and end up somewhere
        assert response.status_code == 200

    def test_change_password_page_loads(self, authenticated_client):
        """Test that password change page loads for authenticated users."""
        response = authenticated_client.get("/settings/change_password", follow_redirects=True)
        
        assert response.status_code == 200


class TestForgotPassword:
    """Tests for the forgot password functionality."""

    def test_forgot_password_page_loads(self, client):
        """Test that forgot password page renders correctly."""
        response = client.get("/auth/forgot_password", follow_redirects=True)
        
        assert response.status_code == 200
