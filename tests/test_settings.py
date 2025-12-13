"""
Unit tests for settings functionality.

Tests cover:
- Settings page rendering
- Priority settings display
"""

import pytest
from kkoala.extensions import db
from kkoala.models import User, Settings, PrioritySetting


class TestSettingsPage:
    """Tests for the settings page."""

    def test_settings_page_displays_current_values(self, authenticated_client, test_user, app):
        """Test that settings page shows current user settings."""
        response = authenticated_client.get("/settings", follow_redirects=True)
        
        assert response.status_code == 200
        # Check for settings-related content
        assert b"Einstellungen" in response.data or b"settings" in response.data.lower()


class TestPrioritySettings:
    """Tests for priority settings management."""

    def test_priority_settings_displayed(self, authenticated_client, test_user, app):
        """Test that priority settings are displayed on settings page."""
        response = authenticated_client.get("/settings", follow_redirects=True)
        
        assert response.status_code == 200
        # Should show priority section
        assert b"priorit" in response.data.lower() or b"Priorit" in response.data


class TestSettingsModel:
    """Tests for settings model directly."""

    def test_settings_values(self, app, test_user):
        """Test that settings are stored correctly."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            
            assert settings is not None
            assert settings.learn_on_saturday == False
            assert settings.learn_on_sunday == False
            assert settings.preferred_learning_time == "18:00"
            assert settings.dark_mode == "system"

    def test_priority_settings_values(self, app, test_user):
        """Test that priority settings are stored correctly."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            priorities = settings.priority_settings
            
            assert len(priorities) == 1
            assert priorities[0].priority_level == 1
            assert priorities[0].max_hours_per_day == 2.0
            assert priorities[0].total_hours_to_learn == 10.0

    def test_update_settings_directly(self, app, test_user):
        """Test updating settings through the model."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            
            settings.dark_mode = "dark"
            settings.learn_on_saturday = True
            db.session.commit()
            
            # Verify changes
            settings = Settings.query.filter_by(user_id=user.id).first()
            assert settings.dark_mode == "dark"
            assert settings.learn_on_saturday == True

    def test_add_priority_directly(self, app, test_user):
        """Test adding priority through the model."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            initial_count = len(settings.priority_settings)
            
            new_priority = PrioritySetting(
                settings_id=settings.id,
                priority_level=2,
                color="#00FF00",
                max_hours_per_day=1.5,
                total_hours_to_learn=8.0
            )
            db.session.add(new_priority)
            db.session.commit()
            
            # Verify addition
            settings = Settings.query.filter_by(user_id=user.id).first()
            assert len(settings.priority_settings) == initial_count + 1

    def test_remove_priority_directly(self, app, test_user):
        """Test removing priority through the model."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            
            # Add a priority first
            new_priority = PrioritySetting(
                settings_id=settings.id,
                priority_level=2,
                color="#00FF00",
                max_hours_per_day=1.5,
                total_hours_to_learn=8.0
            )
            db.session.add(new_priority)
            db.session.commit()
            
            count_before = len(settings.priority_settings)
            
            # Remove it
            db.session.delete(new_priority)
            db.session.commit()
            
            # Verify removal
            settings = Settings.query.filter_by(user_id=user.id).first()
            assert len(settings.priority_settings) == count_before - 1


class TestAccountModel:
    """Tests for account operations through model."""

    def test_delete_user_cascades(self, app, test_user):
        """Test that deleting a user cascades to settings."""
        with app.app_context():
            user = User.query.get(test_user)
            settings_id = user.settings.id
            
            db.session.delete(user)
            db.session.commit()
            
            # Settings should be deleted
            assert Settings.query.get(settings_id) is None
            assert User.query.get(test_user) is None
