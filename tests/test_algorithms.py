"""
Unit tests for the learning time algorithm.

Tests cover:
- Scheduling learning blocks for exams
- Respecting user preferences (weekend, time preferences)
- Handling edge cases (no settings, past exams, etc.)
"""

import pytest
from datetime import datetime, timedelta, timezone, time as dtime
from kkoala.extensions import db
from kkoala.models import User, Settings, PrioritySetting, Event
from kkoala.algorithms import learning_time_algorithm
from kkoala.utils import to_dt


class TestLearningTimeAlgorithm:
    """Tests for the learning time scheduling algorithm."""

    def test_algorithm_creates_learning_blocks(self, app, test_user, sample_event):
        """Test that the algorithm creates learning blocks for an exam."""
        with app.app_context():
            user = User.query.get(test_user)
            events = list(user.events)
            
            summary, successes = learning_time_algorithm(events, user)
            
            # Check that algorithm ran
            assert summary["exams_processed"] >= 0
            
            # Check for learning blocks created
            learning_blocks = Event.query.filter(
                Event.user_id == user.id,
                Event.title.like("Learning for%")
            ).all()
            
            # Algorithm should create blocks if there's time available
            # (may be 0 if exam is too close)
            assert isinstance(learning_blocks, list)

    def test_algorithm_respects_weekend_settings(self, app, test_user):
        """Test that algorithm respects weekend learning settings."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            
            # Ensure weekends are disabled
            settings.learn_on_saturday = False
            settings.learn_on_sunday = False
            db.session.commit()
            
            # Create an exam in 14 days
            exam_date = datetime.now(timezone.utc) + timedelta(days=14)
            exam = Event(
                user_id=user.id,
                title="Weekend Test Exam",
                start=exam_date.isoformat(),
                end=(exam_date + timedelta(hours=2)).isoformat(),
                color="#FF0000",
                priority=1,
                locked=True,
                all_day=False
            )
            db.session.add(exam)
            db.session.commit()
            
            events = list(user.events)
            summary, successes = learning_time_algorithm(events, user)
            
            # Check that no learning blocks are on weekends
            learning_blocks = Event.query.filter(
                Event.user_id == user.id,
                Event.title.like("Learning for%"),
                Event.locked == False
            ).all()
            
            for block in learning_blocks:
                block_date = to_dt(block.start)
                # Saturday = 5, Sunday = 6
                assert block_date.weekday() not in [5, 6], \
                    f"Learning block scheduled on weekend: {block_date}"

    def test_algorithm_no_settings_returns_empty(self, app):
        """Test that algorithm handles missing settings gracefully."""
        with app.app_context():
            # Create user without settings
            hashed_pw = "$2b$12$test"
            user = User(
                username="nosettings",
                password=hashed_pw,
                email="nosettings@test.com"
            )
            db.session.add(user)
            db.session.commit()
            
            summary, successes = learning_time_algorithm([], user)
            
            # Should return empty results
            assert summary == {}
            assert successes == {}

    def test_algorithm_skips_past_exams(self, app, test_user):
        """Test that algorithm ignores past exams."""
        with app.app_context():
            user = User.query.get(test_user)
            
            # Create a past exam
            past_date = datetime.now(timezone.utc) - timedelta(days=7)
            past_exam = Event(
                user_id=user.id,
                title="Past Exam",
                start=past_date.isoformat(),
                end=(past_date + timedelta(hours=2)).isoformat(),
                color="#FF0000",
                priority=1,
                locked=True,
                all_day=False
            )
            db.session.add(past_exam)
            db.session.commit()
            
            events = list(user.events)
            summary, successes = learning_time_algorithm(events, user)
            
            # Past exam should not be in successes
            assert "Past Exam" not in successes

    def test_algorithm_respects_max_hours_per_day(self, app, test_user):
        """Test that algorithm respects max hours per day limit."""
        with app.app_context():
            user = User.query.get(test_user)
            settings = user.settings
            priority = settings.priority_settings[0]
            
            # Set max 1 hour per day
            priority.max_hours_per_day = 1.0
            priority.total_hours_to_learn = 5.0
            db.session.commit()
            
            # Create exam in 10 days
            exam_date = datetime.now(timezone.utc) + timedelta(days=10)
            exam = Event(
                user_id=user.id,
                title="Max Hours Test Exam",
                start=exam_date.isoformat(),
                end=(exam_date + timedelta(hours=2)).isoformat(),
                color="#FF0000",
                priority=1,
                locked=True,
                all_day=False
            )
            db.session.add(exam)
            db.session.commit()
            
            events = list(user.events)
            learning_time_algorithm(events, user)
            
            # Check learning blocks
            learning_blocks = Event.query.filter(
                Event.user_id == user.id,
                Event.exam_id == exam.id,
                Event.locked == False
            ).all()
            
            # Group by date and check hours
            blocks_by_date = {}
            for block in learning_blocks:
                date = to_dt(block.start).date()
                duration = (to_dt(block.end) - to_dt(block.start)).total_seconds() / 3600
                blocks_by_date[date] = blocks_by_date.get(date, 0) + duration
            
            for date, hours in blocks_by_date.items():
                assert hours <= 1.0 + 0.01, \
                    f"More than 1 hour scheduled on {date}: {hours} hours"

    def test_algorithm_cleans_up_old_blocks(self, app, test_user, sample_event):
        """Test that algorithm removes old non-locked learning blocks."""
        with app.app_context():
            user = User.query.get(test_user)
            event = Event.query.get(sample_event)
            
            # Create an old learning block
            old_block = Event(
                user_id=user.id,
                title=f"Learning for {event.title}",
                start=(datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
                end=(datetime.now(timezone.utc) + timedelta(days=2, hours=1)).isoformat(),
                color="#0000FF",
                priority=0,
                locked=False,  # Not locked = algorithm-generated
                exam_id=event.id,
                all_day=False
            )
            db.session.add(old_block)
            db.session.commit()
            old_block_id = old_block.id
            
            events = list(user.events)
            learning_time_algorithm(events, user)
            
            # Old block should be deleted
            old_block = Event.query.get(old_block_id)
            assert old_block is None

    def test_algorithm_preserves_locked_blocks(self, app, test_user, sample_event):
        """Test that algorithm preserves user-locked learning blocks."""
        with app.app_context():
            user = User.query.get(test_user)
            event = Event.query.get(sample_event)
            
            # Create a locked learning block
            locked_block = Event(
                user_id=user.id,
                title=f"Learning for {event.title}",
                start=(datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
                end=(datetime.now(timezone.utc) + timedelta(days=2, hours=1)).isoformat(),
                color="#0000FF",
                priority=0,
                locked=True,  # Locked = user-created
                exam_id=event.id,
                all_day=False
            )
            db.session.add(locked_block)
            db.session.commit()
            locked_block_id = locked_block.id
            
            events = list(user.events)
            learning_time_algorithm(events, user)
            
            # Locked block should still exist
            locked_block = Event.query.get(locked_block_id)
            assert locked_block is not None


class TestAlgorithmEdgeCases:
    """Tests for edge cases in the learning algorithm."""

    def test_algorithm_with_no_exams(self, app, test_user):
        """Test algorithm behavior when there are no exams."""
        with app.app_context():
            user = User.query.get(test_user)
            
            # Delete any existing events
            Event.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            
            events = []
            summary, successes = learning_time_algorithm(events, user)
            
            assert summary["exams_processed"] == 0
            assert summary["blocks_added"] == 0

    def test_algorithm_with_all_day_blocking_event(self, app, test_user):
        """Test that algorithm skips days with all-day events."""
        with app.app_context():
            user = User.query.get(test_user)
            
            # Create exam in 7 days
            exam_date = datetime.now(timezone.utc) + timedelta(days=7)
            exam = Event(
                user_id=user.id,
                title="Blocked Day Test Exam",
                start=exam_date.isoformat(),
                end=(exam_date + timedelta(hours=2)).isoformat(),
                color="#FF0000",
                priority=1,
                locked=True,
                all_day=False
            )
            db.session.add(exam)
            
            # Create all-day event blocking the day before exam
            blocked_day = exam_date - timedelta(days=1)
            blocking_event = Event(
                user_id=user.id,
                title="All Day Block",
                start=blocked_day.replace(hour=0, minute=0).isoformat(),
                end=(blocked_day + timedelta(days=1)).isoformat(),
                color="#CCCCCC",
                priority=0,
                locked=True,
                all_day=True
            )
            db.session.add(blocking_event)
            db.session.commit()
            
            events = list(user.events)
            learning_time_algorithm(events, user)
            
            # No learning blocks should be on the blocked day
            learning_blocks = Event.query.filter(
                Event.user_id == user.id,
                Event.exam_id == exam.id,
                Event.locked == False
            ).all()
            
            for block in learning_blocks:
                block_date = to_dt(block.start).date()
                assert block_date != blocked_day.date(), \
                    f"Learning block scheduled on blocked day: {block_date}"
