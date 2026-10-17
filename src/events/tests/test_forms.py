import json
from datetime import date
from unittest.mock import patch

from django.test import TestCase

from events.forms import EventForm
from events.models import Event


FIXED_TODAY = date(2026, 10, 17)


class EventFormTests(TestCase):
    """Test event and timeslot form validation."""

    def setUp(self):
        self.localdate_patcher = patch(
            "events.forms.timezone.localdate",
            return_value=FIXED_TODAY,
        )
        self.localdate_patcher.start()
        self.addCleanup(self.localdate_patcher.stop)

    @staticmethod
    def form_data(**overrides) -> dict:
        """Create valid form data for a test case."""
        data = {
            "title": "Test Event",
            "description": "Description",
            "location": "Frankfurt",
            "start_date": "2026-10-18",
            "end_date": "2026-10-19",
            "timeslots": json.dumps(
                [
                    {
                        "start": "10:00",
                        "end": "12:00",
                        "duration": "120",
                        "category": "Workshop",
                    }
                ]
            ),
        }
        data.update(overrides)
        return data

    def test_form_valid(self):
        """Accept a correctly completed multi-day event form."""
        form = EventForm(data=self.form_data())

        self.assertTrue(form.is_valid())

    def test_single_day_event_is_valid(self):
        """Accept an event that starts and ends on the same day."""
        form = EventForm(
            data=self.form_data(
                start_date="2026-10-17",
                end_date="2026-10-17",
            )
        )

        self.assertTrue(form.is_valid())

    def test_start_date_in_past_is_invalid(self):
        """Reject a new event whose start date is in the past."""
        form = EventForm(
            data=self.form_data(
                start_date="2026-10-16",
                end_date="2026-10-18",
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)

    def test_five_calendar_year_limit_including_leap_day(self):
        """Enforce the inclusive five-year limit from February 29."""
        with patch(
            "events.forms.timezone.localdate",
            return_value=date(2028, 2, 29),
        ):
            form_at_limit = EventForm(
                data=self.form_data(
                    start_date="2033-02-28",
                    end_date="2033-02-28",
                )
            )
            form_after_limit = EventForm(
                data=self.form_data(
                    start_date="2033-02-28",
                    end_date="2033-03-01",
                )
            )
            form_with_late_start = EventForm(
                data=self.form_data(
                    start_date="2033-03-01",
                    end_date="2033-03-01",
                )
            )

            self.assertTrue(form_at_limit.is_valid())
            self.assertFalse(form_after_limit.is_valid())
            self.assertIn("end_date", form_after_limit.errors)
            self.assertFalse(form_with_late_start.is_valid())
            self.assertIn("start_date", form_with_late_start.errors)

    def test_existing_past_start_date_may_remain_unchanged(self):
        """Allow an existing past start date only when it is unchanged."""
        event = Event.objects.create(
            title="Existing Event",
            description="Description",
            location="Frankfurt",
            start_date=date(2026, 10, 15),
            end_date=date(2026, 10, 16),
        )
        form = EventForm(
            instance=event,
            data=self.form_data(
                start_date="2026-10-15",
                end_date="2026-10-16",
            ),
        )
        form_with_changed_start = EventForm(
            instance=event,
            data=self.form_data(
                start_date="2026-10-14",
                end_date="2026-10-16",
            ),
        )

        self.assertTrue(form.is_valid())
        self.assertFalse(form_with_changed_start.is_valid())
        self.assertIn("start_date", form_with_changed_start.errors)

    def test_timeslot_start_after_end(self):
        """Reject a timeslot whose start time is after its end time."""
        form = EventForm(
            data=self.form_data(
                timeslots=json.dumps(
                    [
                        {
                            "start": "14:00",
                            "end": "12:00",
                            "duration": "120",
                            "category": "Workshop",
                        }
                    ]
                )
            )
        )

        self.assertFalse(form.is_valid())

    def test_timeslot_missing_category(self):
        """Reject a timeslot without a category."""
        form = EventForm(
            data=self.form_data(
                timeslots=json.dumps(
                    [
                        {
                            "start": "10:00",
                            "end": "12:00",
                            "duration": "120",
                            "category": "",
                        }
                    ]
                )
            )
        )

        self.assertFalse(form.is_valid())

    def test_timeslot_invalid_duration(self):
        """Reject a timeslot with a negative duration."""
        form = EventForm(
            data=self.form_data(
                timeslots=json.dumps(
                    [
                        {
                            "start": "10:00",
                            "end": "12:00",
                            "duration": "-5",
                            "category": "Workshop",
                        }
                    ]
                )
            )
        )

        self.assertFalse(form.is_valid())

    def test_invalid_json(self):
        """Reject malformed JSON in the timeslot field."""
        form = EventForm(data=self.form_data(timeslots="{broken"))

        self.assertFalse(form.is_valid())

    def test_start_date_after_end_date(self):
        """Reject an end date before the start date."""
        form = EventForm(
            data=self.form_data(
                start_date="2026-10-19",
                end_date="2026-10-18",
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)
