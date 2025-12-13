"""
Pytest configuration and fixtures for KantiKoala LernApp tests.

This module provides shared fixtures for:
- Flask application instance with test configuration
- Database setup and teardown
- Test user creation and authentication
- Common test data
"""

import pytest
from kkoala import create_app
from kkoala.extensions import db, bcrypt
from kkoala.models import (
    User, Settings, PrioritySetting, Event, 
    Semester, Subject, Grade, ToDoCategory, ToDoItem
)


@pytest.fixture(scope="function")
def app():
    """
    Create and configure a new app instance for each test.
    Uses in-memory SQLite database for isolation.
    """
    app = create_app("kkoala.config.TestConfig")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def test_user(app):
    """
    Create a test user with default settings.
    Returns the user object.
    """
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash("testpassword123").decode("utf-8")
        user = User(
            username="testuser",
            password=hashed_password,
            email="test@example.com"
        )
        db.session.add(user)
        db.session.commit()
        
        # Create default settings for the user
        settings = Settings(
            user_id=user.id,
            learn_on_saturday=False,
            learn_on_sunday=False,
            preferred_learning_time="18:00",
            study_block_color="#0000FF",
            import_color="#6C757D",
            dark_mode="system"
        )
        db.session.add(settings)
        db.session.commit()  # Commit settings first to get the ID
        
        # Add default priority settings
        priority = PrioritySetting(
            settings_id=settings.id,
            priority_level=1,
            color="#FF0000",
            max_hours_per_day=2.0,
            total_hours_to_learn=10.0
        )
        db.session.add(priority)
        db.session.commit()
        
        # Return user id to fetch fresh instance in tests
        user_id = user.id
        
    return user_id


@pytest.fixture(scope="function")
def authenticated_client(client, test_user, app):
    """
    A test client with an authenticated session.
    """
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
        sess["csrf_token"] = "test-csrf-token"
    return client


@pytest.fixture(scope="function")
def sample_event(app, test_user):
    """
    Create a sample event (exam) for testing.
    Returns the event id.
    """
    from datetime import datetime, timedelta, timezone
    
    with app.app_context():
        user = User.query.get(test_user)
        exam_date = datetime.now(timezone.utc) + timedelta(days=7)
        
        event = Event(
            user_id=user.id,
            title="Math Exam",
            start=exam_date.isoformat(),
            end=(exam_date + timedelta(hours=2)).isoformat(),
            color="#FF0000",
            priority=1,
            locked=True,
            all_day=False
        )
        db.session.add(event)
        db.session.commit()
        
        return event.id


@pytest.fixture(scope="function")
def sample_semester(app, test_user):
    """
    Create a sample semester with subjects and grades.
    Returns the semester id.
    """
    with app.app_context():
        user = User.query.get(test_user)
        
        semester = Semester(
            user_id=user.id,
            name="Frühlingssemester 2025",
            is_current=True
        )
        db.session.add(semester)
        db.session.commit()
        
        subject = Subject(
            semester_id=semester.id,
            name="Mathematik",
            counts_towards_average=True
        )
        db.session.add(subject)
        db.session.commit()
        
        grade = Grade(
            subject_id=subject.id,
            name="Prüfung 1",
            value=5.5,
            weight=1.0,
            counts=True
        )
        db.session.add(grade)
        db.session.commit()
        
        return semester.id


@pytest.fixture(scope="function")
def sample_todo(app, test_user):
    """
    Create a sample to-do category with items.
    Returns the category id.
    """
    with app.app_context():
        user = User.query.get(test_user)
        
        category = ToDoCategory(
            user_id=user.id,
            name="Hausaufgaben"
        )
        db.session.add(category)
        db.session.commit()
        
        item = ToDoItem(
            category_id=category.id,
            description="Mathe Übungen fertigstellen"
        )
        db.session.add(item)
        db.session.commit()
        
        return category.id
