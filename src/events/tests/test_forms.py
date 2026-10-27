import json
from calendar import isleap
from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from events.forms import EventForm
from events.models import Event


class EventFormTests(TestCase):
    """Test event and timeslot form validation."""

    @staticmethod
    def form_data(**overrides) -> dict:
        """Create valid form data for a test case."""
        today = timezone.localdate()
        data = {
            "title": "Test Event",
            "description": "Description",
            "location": "Frankfurt",
            "start_date": (today + timedelta(days=1)).isoformat(),
            "end_date": (today + timedelta(days=2)).isoformat(),
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
        event_date = (timezone.localdate() + timedelta(days=1)).isoformat()
        form = EventForm(
            data=self.form_data(
                end_date=event_date,
            )
        )

        self.assertTrue(form.is_valid())

    def test_start_date_in_past_is_invalid(self):
        """Reject a new event whose start date is in the past."""
        form = EventForm(
            data=self.form_data(
                start_date=(timezone.localdate() - timedelta(days=1)).isoformat(),
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)

    def test_five_calendar_year_limit_including_leap_day(self):
        """Enforce the inclusive five-year limit from February 29."""
        current_year = timezone.localdate().year
        leap_year = next(
            year for year in range(current_year, current_year + 8) if isleap(year)
        )
        leap_day = date(leap_year, 2, 29)
        latest_date = date(leap_year + 5, 2, 28)
        date_after_limit = latest_date + timedelta(days=1)

        with patch(
            "events.forms.timezone.localdate",
            return_value=leap_day,
        ):
            form_at_limit = EventForm(
                data=self.form_data(
                    start_date=latest_date.isoformat(),
                    end_date=latest_date.isoformat(),
                )
            )
            form_after_limit = EventForm(
                data=self.form_data(
                    start_date=latest_date.isoformat(),
                    end_date=date_after_limit.isoformat(),
                )
            )
            form_with_late_start = EventForm(
                data=self.form_data(
                    start_date=date_after_limit.isoformat(),
                    end_date=date_after_limit.isoformat(),
                )
            )

            self.assertTrue(form_at_limit.is_valid())
            self.assertFalse(form_after_limit.is_valid())
            self.assertIn("end_date", form_after_limit.errors)
            self.assertFalse(form_with_late_start.is_valid())
            self.assertIn("start_date", form_with_late_start.errors)

    def test_existing_past_start_date_may_remain_unchanged(self):
        """Allow an existing past start date only when it is unchanged."""
        today = timezone.localdate()
        existing_start_date = today - timedelta(days=2)
        existing_end_date = today - timedelta(days=1)
        event = Event.objects.create(
            title="Existing Event",
            description="Description",
            location="Frankfurt",
            start_date=existing_start_date,
            end_date=existing_end_date,
        )
        form = EventForm(
            instance=event,
            data=self.form_data(
                start_date=existing_start_date.isoformat(),
                end_date=existing_end_date.isoformat(),
            ),
        )
        form_with_changed_start = EventForm(
            instance=event,
            data=self.form_data(
                start_date=(existing_start_date - timedelta(days=1)).isoformat(),
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
        self.assertIn("timeslots", form.errors)

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
        self.assertIn("timeslots", form.errors)

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
        self.assertIn("timeslots", form.errors)

    def test_invalid_json(self):
        """Reject malformed JSON in the timeslot field."""
        form = EventForm(data=self.form_data(timeslots="{broken"))

        self.assertFalse(form.is_valid())
        self.assertIn("timeslots", form.errors)

    def test_missing_required_date_fields_are_invalid(self):
        """Reject missing required dates and attach errors to their fields."""
        for field_name in ("start_date", "end_date"):
            with self.subTest(field=field_name):
                form = EventForm(data=self.form_data(**{field_name: ""}))

                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_start_date_after_end_date(self):
        """Reject an end date before the start date."""
        form = EventForm(
            data=self.form_data(
                end_date=timezone.localdate().isoformat(),
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)
