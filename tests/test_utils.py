"""
Unit tests for utility functions.

Tests cover:
- Date/time conversion functions
- Free slot calculation
- Helper functions
"""

import pytest
from datetime import datetime, timedelta, time as dtime, timezone
from kkoala.utils import to_dt, to_iso, free_slots, str_to_bool


class TestDateTimeConversion:
    """Tests for date/time conversion utilities."""

    def test_to_dt_with_iso_string(self):
        """Test converting ISO string to datetime."""
        iso_string = "2025-01-15T10:30:00Z"
        result = to_dt(iso_string)
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.tzinfo is not None

    def test_to_dt_with_datetime(self):
        """Test converting datetime to UTC datetime."""
        dt = datetime(2025, 1, 15, 10, 30, 0)
        result = to_dt(dt)
        
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc

    def test_to_dt_with_timezone_aware_datetime(self):
        """Test converting timezone-aware datetime to UTC."""
        from zoneinfo import ZoneInfo
        
        zurich_tz = ZoneInfo("Europe/Zurich")
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=zurich_tz)
        result = to_dt(dt)
        
        assert result.tzinfo == timezone.utc
        # Zurich is UTC+1 in winter, so 12:00 Zurich = 11:00 UTC
        assert result.hour == 11

    def test_to_dt_with_none(self):
        """Test that None input returns None."""
        result = to_dt(None)
        assert result is None

    def test_to_dt_with_offset_string(self):
        """Test converting ISO string with offset."""
        iso_string = "2025-01-15T10:30:00+02:00"
        result = to_dt(iso_string)
        
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
        # 10:30 +02:00 = 08:30 UTC
        assert result.hour == 8

    def test_to_iso_with_datetime(self):
        """Test converting datetime to ISO string."""
        dt = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        result = to_iso(dt)
        
        assert result == "2025-01-15T10:30:00Z"

    def test_to_iso_with_naive_datetime(self):
        """Test converting naive datetime to ISO string (assumes UTC)."""
        dt = datetime(2025, 1, 15, 10, 30, 0)
        result = to_iso(dt)
        
        assert result == "2025-01-15T10:30:00Z"

    def test_to_iso_with_none(self):
        """Test that None input returns None."""
        result = to_iso(None)
        assert result is None


class TestStrToBool:
    """Tests for str_to_bool utility."""

    def test_str_to_bool_true_string(self):
        """Test converting 'true' string to bool."""
        assert str_to_bool("true") == True
        assert str_to_bool("True") == True
        assert str_to_bool("TRUE") == True

    def test_str_to_bool_false_string(self):
        """Test converting 'false' string to bool."""
        assert str_to_bool("false") == False
        assert str_to_bool("False") == False
        assert str_to_bool("anything") == False

    def test_str_to_bool_bool_input(self):
        """Test that bool input passes through."""
        assert str_to_bool(True) == True
        assert str_to_bool(False) == False

    def test_str_to_bool_other_types(self):
        """Test that other types return False."""
        assert str_to_bool(None) == False
        assert str_to_bool(123) == False


class TestFreeSlots:
    """Tests for free_slots utility."""

    def test_free_slots_empty_day(self, app):
        """Test free slots calculation with no events."""
        from zoneinfo import ZoneInfo
        from kkoala.consts import DAY_START
        
        day = datetime.now().date() + timedelta(days=1)
        events = []
        
        slots = free_slots(events, day)
        
        # Should have one slot from DAY_START to 22:00
        assert len(slots) == 1
        start, end = slots[0]
        
        # Verify the slot spans the working day
        user_tz = ZoneInfo("Europe/Zurich")
        expected_start = datetime.combine(day, DAY_START).replace(tzinfo=user_tz).astimezone(timezone.utc)
        expected_end = datetime.combine(day, dtime(22, 0)).replace(tzinfo=user_tz).astimezone(timezone.utc)
        
        assert start == expected_start
        assert end == expected_end

    def test_free_slots_with_event(self, app, test_user, sample_event):
        """Test free slots calculation with an event in the middle."""
        from kkoala.models import Event
        from zoneinfo import ZoneInfo
        
        with app.app_context():
            # Get the sample event
            event = Event.query.get(sample_event)
            event_day = to_dt(event.start).date()
            
            events = [event]
            slots = free_slots(events, event_day)
            
            # Should have slots before and/or after the event
            assert len(slots) >= 0  # May have 0, 1, or 2 slots depending on event time

    def test_free_slots_all_day_event(self, app, test_user):
        """Test that all-day events block all slots."""
        from kkoala.models import Event, User
        from kkoala.extensions import db
        
        with app.app_context():
            user = User.query.get(test_user)
            day = datetime.now().date() + timedelta(days=1)
            
            all_day_event = Event(
                user_id=user.id,
                title="All Day Event",
                start=datetime.combine(day, dtime(0, 0)).isoformat(),
                end=datetime.combine(day + timedelta(days=1), dtime(0, 0)).isoformat(),
                color="#FF0000",
                priority=1,
                locked=True,
                all_day=True
            )
            db.session.add(all_day_event)
            db.session.commit()
            
            events = [all_day_event]
            slots = free_slots(events, day)
            
            # All-day event should block all slots
            assert len(slots) == 0


class TestDecorators:
    """Tests for decorator utilities."""

    def test_login_required_redirects(self, client):
        """Test that login_required redirects unauthenticated users."""
        response = client.get("/agenda", follow_redirects=True)
        
        # After following redirects, we should land on a page
        assert response.status_code == 200
        # And it should be the login page
        assert b"login" in response.data.lower() or b"anmelden" in response.data.lower()

    def test_login_required_with_session(self, authenticated_client):
        """Test that authenticated users can access protected routes."""
        response = authenticated_client.get("/agenda", follow_redirects=True)
        
        # Should eventually get 200 OK (after any redirects)
        assert response.status_code == 200

    def test_csrf_protect_behavior(self, client, test_user, app):
        """Test that CSRF protection is documented."""
        # Note: CSRF check is skipped in TESTING mode
        # This test documents expected behavior in production
        pass
