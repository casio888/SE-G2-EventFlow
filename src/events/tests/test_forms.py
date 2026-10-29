from calendar import isleap
from datetime import date, time, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from events.forms import EventForm, TimeslotForm, TimeslotFormSet
from events.models import Event, Timeslot


class EventFormTests(TestCase):
    """Test event form validation."""

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


class TimeslotFormTests(TestCase):
    """Test creating and updating individual timeslots."""

    def setUp(self):
        event_date = timezone.localdate() + timedelta(days=1)
        self.event = Event.objects.create(
            title="Managed Event",
            description="Description",
            location="Frankfurt",
            start_date=event_date,
            end_date=event_date,
        )

    @staticmethod
    def form_data(**overrides) -> dict:
        """Create valid individual timeslot form data."""
        data = {
            "category": "Workshop",
            "start": "09:00",
            "end": "10:30",
        }
        data.update(overrides)
        return data

    def test_form_creates_timeslot_with_calculated_duration(self):
        """Create a valid timeslot and calculate its duration."""
        form = TimeslotForm(data=self.form_data())

        self.assertTrue(form.is_valid())
        timeslot = form.save(commit=False)
        timeslot.event = self.event
        timeslot.save()

        self.assertEqual(timeslot.duration, 90)
        self.assertEqual(timeslot.category, "Workshop")

    def test_form_rejects_end_not_later_than_start(self):
        """Reject equal or decreasing times and attach the error to end."""
        for end in ("09:00", "08:59"):
            with self.subTest(end=end):
                form = TimeslotForm(data=self.form_data(end=end))

                self.assertFalse(form.is_valid())
                self.assertIn("end", form.errors)

    def test_form_rejects_missing_or_invalid_times(self):
        """Reject missing and malformed start and end values."""
        invalid_values = [
            ("start", ""),
            ("end", ""),
            ("start", "25:00"),
            ("end", "not-a-time"),
        ]

        for field_name, value in invalid_values:
            with self.subTest(field=field_name, value=value):
                form = TimeslotForm(
                    data=self.form_data(**{field_name: value})
                )

                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_form_rejects_blank_category(self):
        """Reject an empty or whitespace-only category."""
        for category in ("", "   "):
            with self.subTest(category=category):
                form = TimeslotForm(data=self.form_data(category=category))

                self.assertFalse(form.is_valid())
                self.assertIn("category", form.errors)

    def test_submitted_duration_is_ignored_and_recalculated(self):
        """Derive duration from validated times instead of submitted data."""
        form = TimeslotForm(
            data=self.form_data(duration="999"),
        )

        self.assertTrue(form.is_valid())
        timeslot = form.save(commit=False)

        self.assertEqual(timeslot.duration, 90)

    def test_form_updates_category_and_times(self):
        """Update editable fields and recalculate the duration."""
        timeslot = Timeslot.objects.create(
            event=self.event,
            start=time(9, 0),
            end=time(10, 0),
            duration=60,
            category="Workshop",
        )
        form = TimeslotForm(
            instance=timeslot,
            data=self.form_data(
                category="Panel",
                start="11:00",
                end="12:45",
            ),
        )

        self.assertTrue(form.is_valid())
        updated_timeslot = form.save()

        self.assertEqual(updated_timeslot.start, time(11, 0))
        self.assertEqual(updated_timeslot.end, time(12, 45))
        self.assertEqual(updated_timeslot.duration, 105)
        self.assertEqual(updated_timeslot.category, "Panel")


class TimeslotFormSetTests(TestCase):
    """Test the structural validation of event timeslot formsets."""

    def test_formset_requires_valid_management_data(self):
        """Reject malformed formset submissions without raising an exception."""
        event = Event()
        formset = TimeslotFormSet(data={}, instance=event, prefix="timeslots")

        self.assertFalse(formset.is_valid())
        self.assertTrue(formset.non_form_errors())
