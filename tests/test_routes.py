"""
Unit tests for application routes.

Tests cover:
- Main routes (home, agenda, etc.)
- API endpoints
- Error handling
"""

import pytest
import json
from kkoala.extensions import db
from kkoala.models import User, Event, Semester, ToDoCategory


class TestMainRoutes:
    """Tests for main application routes."""

    def test_home_page_loads(self, authenticated_client):
        """Test that the home page loads for authenticated users."""
        response = authenticated_client.get("/", follow_redirects=True)
        
        assert response.status_code == 200

    def test_agenda_page_loads(self, authenticated_client):
        """Test that the agenda page loads correctly."""
        response = authenticated_client.get("/agenda", follow_redirects=True)
        
        assert response.status_code == 200

    def test_grades_page_loads(self, authenticated_client):
        """Test that the grades page loads correctly."""
        response = authenticated_client.get("/noten", follow_redirects=True)
        
        assert response.status_code == 200

    def test_todo_page_loads(self, authenticated_client):
        """Test that the to-do page loads correctly."""
        response = authenticated_client.get("/todo", follow_redirects=True)
        
        assert response.status_code == 200

    def test_settings_page_loads(self, authenticated_client):
        """Test that the settings page loads correctly."""
        response = authenticated_client.get("/settings", follow_redirects=True)
        
        assert response.status_code == 200

    def test_lerntipps_page_loads(self, authenticated_client):
        """Test that the learning tips page loads correctly."""
        response = authenticated_client.get("/lerntipps", follow_redirects=True)
        
        assert response.status_code == 200

    def test_lerntimer_page_loads(self, authenticated_client):
        """Test that the learning timer page loads correctly."""
        response = authenticated_client.get("/lerntimer", follow_redirects=True)
        
        assert response.status_code == 200


class TestProtectedRoutes:
    """Tests for route protection."""

    def test_agenda_requires_login(self, client):
        """Test that agenda page requires authentication."""
        response = client.get("/agenda", follow_redirects=True)
        
        # Should redirect to login page (200 after following redirects)
        assert response.status_code == 200
        # Should contain login-related content
        assert b"login" in response.data.lower() or b"anmelden" in response.data.lower()

    def test_grades_requires_login(self, client):
        """Test that grades page requires authentication."""
        response = client.get("/noten", follow_redirects=True)
        
        assert response.status_code == 200
        assert b"login" in response.data.lower() or b"anmelden" in response.data.lower()

    def test_settings_requires_login(self, client):
        """Test that settings page requires authentication."""
        response = client.get("/settings", follow_redirects=True)
        
        assert response.status_code == 200
        assert b"login" in response.data.lower() or b"anmelden" in response.data.lower()


class TestEventAPI:
    """Tests for event-related API endpoints."""

    def test_get_events(self, authenticated_client, sample_event, app):
        """Test fetching events via API."""
        response = authenticated_client.get("/api/events", follow_redirects=True)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_create_event(self, authenticated_client, app):
        """Test creating an event via API."""
        with authenticated_client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "test-token")
        
        event_data = {
            "title": "New Test Event",
            "start": "2025-02-01T10:00:00Z",
            "end": "2025-02-01T12:00:00Z",
            "color": "#FF0000",
            "priority": 1,
            "allDay": False,
            "recurrence": "none"
        }
        
        response = authenticated_client.post(
            "/api/events",
            data=json.dumps(event_data),
            content_type="application/json",
            headers={"X-CSRF-Token": csrf_token},
            follow_redirects=True
        )
        
        # Should succeed - 201 Created
        assert response.status_code == 201

    def test_delete_event(self, authenticated_client, sample_event, app):
        """Test deleting an event via API."""
        with authenticated_client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "test-token")
        
        response = authenticated_client.delete(
            f"/api/events/{sample_event}",
            headers={"X-CSRF-Token": csrf_token},
            follow_redirects=True
        )
        
        # Should succeed
        assert response.status_code == 200


class TestGradesAPI:
    """Tests for grades-related functionality."""

    def test_grades_page_shows_content(self, authenticated_client, sample_semester):
        """Test that grades page displays content."""
        response = authenticated_client.get("/noten", follow_redirects=True)
        
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_page(self, authenticated_client):
        """Test that 404 page is returned for non-existent routes."""
        response = authenticated_client.get("/nonexistent-page-12345", follow_redirects=True)
        
        assert response.status_code == 404

    def test_api_returns_error_without_auth(self, client):
        """Test that API returns error for unauthenticated requests."""
        response = client.get("/api/events", follow_redirects=True)
        
        # After redirects, should be on login page or get error
        assert response.status_code in [200, 401]


class TestStaticFiles:
    """Tests for static file serving."""

    def test_robots_txt(self, client):
        """Test that robots.txt is served."""
        response = client.get("/robots.txt", follow_redirects=True)
        
        assert response.status_code == 200

    def test_favicon(self, client):
        """Test that favicon is served."""
        response = client.get("/favicon.ico", follow_redirects=True)
        
        assert response.status_code == 200
