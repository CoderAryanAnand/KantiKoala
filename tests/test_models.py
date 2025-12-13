"""
Unit tests for database models.

Tests cover:
- Model creation and relationships
- Data integrity and constraints
- Cascade delete behavior
"""

import pytest
from kkoala.extensions import db, bcrypt
from kkoala.models import (
    User, Settings, PrioritySetting, Event,
    Semester, Subject, Grade, ToDoCategory, ToDoItem
)


class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self, app):
        """Test creating a new user."""
        with app.app_context():
            hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")
            user = User(
                username="newuser",
                password=hashed_pw,
                email="newuser@example.com"
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == "newuser"
            assert user.email == "newuser@example.com"

    def test_unique_username(self, app, test_user):
        """Test that duplicate usernames are rejected."""
        with app.app_context():
            hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")
            duplicate_user = User(
                username="testuser",  # Same as test_user
                password=hashed_pw,
                email="different@example.com"
            )
            db.session.add(duplicate_user)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

    def test_unique_email(self, app, test_user):
        """Test that duplicate emails are rejected."""
        with app.app_context():
            hashed_pw = bcrypt.generate_password_hash("password123").decode("utf-8")
            duplicate_user = User(
                username="differentuser",
                password=hashed_pw,
                email="test@example.com"  # Same as test_user
            )
            db.session.add(duplicate_user)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

    def test_user_relationships(self, app, test_user):
        """Test that user relationships are properly set up."""
        with app.app_context():
            user = User.query.get(test_user)
            
            assert user.settings is not None
            assert user.events is not None
            assert user.semesters is not None
            assert user.todo_categories is not None


class TestSettingsModel:
    """Tests for the Settings model."""

    def test_settings_defaults(self, app, test_user):
        """Test that settings have correct default values."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            
            assert settings.learn_on_saturday == False
            assert settings.learn_on_sunday == False
            assert settings.preferred_learning_time == "18:00"
            assert settings.dark_mode == "system"

    def test_priority_settings_relationship(self, app, test_user):
        """Test priority settings relationship."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            
            assert len(settings.priority_settings) == 1
            priority = settings.priority_settings[0]
            assert priority.priority_level == 1
            assert priority.max_hours_per_day == 2.0


class TestEventModel:
    """Tests for the Event model."""

    def test_create_event(self, app, test_user):
        """Test creating a new event."""
        from datetime import datetime, timezone
        
        with app.app_context():
            user = User.query.get(test_user)
            event = Event(
                user_id=user.id,
                title="Test Event",
                start=datetime.now(timezone.utc).isoformat(),
                color="#FF0000",
                priority=1,
                locked=True,
                all_day=False
            )
            db.session.add(event)
            db.session.commit()
            
            assert event.id is not None
            assert event.title == "Test Event"

    def test_event_user_relationship(self, app, sample_event):
        """Test event-user relationship."""
        with app.app_context():
            event = Event.query.get(sample_event)
            
            assert event.user is not None
            assert event.user.username == "testuser"


class TestSemesterModel:
    """Tests for the Semester/Subject/Grade models."""

    def test_semester_hierarchy(self, app, sample_semester):
        """Test semester -> subject -> grade hierarchy."""
        with app.app_context():
            semester = Semester.query.get(sample_semester)
            
            assert semester.name == "Frühlingssemester 2025"
            assert len(semester.subjects) == 1
            
            subject = semester.subjects[0]
            assert subject.name == "Mathematik"
            assert len(subject.grades) == 1
            
            grade = subject.grades[0]
            assert grade.value == 5.5

    def test_cascade_delete_semester(self, app, sample_semester):
        """Test that deleting a semester cascades to subjects and grades."""
        with app.app_context():
            semester = Semester.query.get(sample_semester)
            subject_id = semester.subjects[0].id
            grade_id = semester.subjects[0].grades[0].id
            
            db.session.delete(semester)
            db.session.commit()
            
            assert Subject.query.get(subject_id) is None
            assert Grade.query.get(grade_id) is None


class TestToDoModel:
    """Tests for the ToDoCategory/ToDoItem models."""

    def test_todo_hierarchy(self, app, sample_todo):
        """Test category -> item hierarchy."""
        with app.app_context():
            category = ToDoCategory.query.get(sample_todo)
            
            assert category.name == "Hausaufgaben"
            assert len(category.items) == 1
            assert category.items[0].description == "Mathe Übungen fertigstellen"

    def test_cascade_delete_category(self, app, sample_todo):
        """Test that deleting a category cascades to items."""
        with app.app_context():
            category = ToDoCategory.query.get(sample_todo)
            item_id = category.items[0].id
            
            db.session.delete(category)
            db.session.commit()
            
            assert ToDoItem.query.get(item_id) is None
