import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from events.forms import EventForm
from events.models import Event


class EventFormTests(TestCase):
    """Test event and timeslot form validation."""

    @staticmethod
    def timeslot(**overrides) -> dict:
        """Create valid timeslot data for a test case."""
        data = {
            "start": "10:00",
            "end": "12:00",
            "duration": "120",
            "category": "Workshop",
        }
        data.update(overrides)
        return data

    @classmethod
    def form_data(cls, **overrides) -> dict:
        """Create valid event form data with stable future dates."""
        start_date = timezone.localdate() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        data = {
            "title": "Test Event",
            "description": "Description",
            "location": "Frankfurt",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timeslots": json.dumps([cls.timeslot()]),
        }
        data.update(overrides)
        return data

    def test_form_valid(self):
        """Accept a correctly completed form."""
        form = EventForm(data=self.form_data())

        self.assertTrue(form.is_valid())

    def test_editing_event_validates_and_saves_valid_timeslot(self):
        """Validate and save a valid timeslot while editing an event."""
        start_date = timezone.localdate() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        event = Event.objects.create(
            title="Existing Event",
            description="Description",
            location="Frankfurt",
            start_date=start_date,
            end_date=end_date,
        )
        form = EventForm(
            instance=event,
            data=self.form_data(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
            ),
        )

        self.assertTrue(form.is_valid())
        saved_event = form.save()
        self.assertEqual(saved_event.pk, event.pk)
        self.assertEqual(saved_event.timeslots.count(), 1)

    def test_timeslot_json_must_contain_a_list_of_objects(self):
        """Reject valid JSON with an unsupported structure."""
        invalid_structures = [None, {}, "timeslot", [None], ["timeslot"]]

        for structure in invalid_structures:
            with self.subTest(structure=structure):
                form = EventForm(
                    data=self.form_data(timeslots=json.dumps(structure))
                )

                self.assertFalse(form.is_valid())
                self.assertIn("timeslots", form.errors)

    def test_timeslot_start_and_end_must_be_present_and_valid(self):
        """Reject missing, malformed, and non-string time values."""
        timeslot_without_start = self.timeslot()
        timeslot_without_start.pop("start")
        timeslot_without_end = self.timeslot()
        timeslot_without_end.pop("end")
        invalid_timeslots = [
            timeslot_without_start,
            timeslot_without_end,
            self.timeslot(start=""),
            self.timeslot(end=""),
            self.timeslot(start="25:00"),
            self.timeslot(end="not-a-time"),
            self.timeslot(start=10),
            self.timeslot(end=[12, 0]),
        ]

        for timeslot in invalid_timeslots:
            with self.subTest(timeslot=timeslot):
                form = EventForm(
                    data=self.form_data(timeslots=json.dumps([timeslot]))
                )

                self.assertFalse(form.is_valid())
                self.assertIn("timeslots", form.errors)

    def test_timeslot_start_must_be_before_end(self):
        """Reject timeslots that start at or after their end time."""
        for start, end in [("14:00", "12:00"), ("12:00", "12:00")]:
            with self.subTest(start=start, end=end):
                form = EventForm(
                    data=self.form_data(
                        timeslots=json.dumps(
                            [self.timeslot(start=start, end=end)]
                        )
                    )
                )

                self.assertFalse(form.is_valid())
                self.assertIn("timeslots", form.errors)

    def test_explicit_duration_must_be_a_positive_integer(self):
        """Reject non-integer, zero, and negative explicit durations."""
        invalid_durations = ["-5", "0", 0, "invalid", 30.5, False]

        for duration in invalid_durations:
            with self.subTest(duration=duration):
                form = EventForm(
                    data=self.form_data(
                        timeslots=json.dumps(
                            [self.timeslot(duration=duration)]
                        )
                    )
                )

                self.assertFalse(form.is_valid())
                self.assertIn("timeslots", form.errors)

    def test_duration_may_equal_but_not_exceed_available_time(self):
        """Accept the duration boundary and reject longer durations."""
        form_at_limit = EventForm(
            data=self.form_data(
                timeslots=json.dumps([self.timeslot(duration=120)])
            )
        )
        form_above_limit = EventForm(
            data=self.form_data(
                timeslots=json.dumps([self.timeslot(duration="121")])
            )
        )

        self.assertTrue(form_at_limit.is_valid())
        self.assertFalse(form_above_limit.is_valid())
        self.assertIn("timeslots", form_above_limit.errors)

    def test_missing_or_empty_duration_is_calculated_automatically(self):
        """Calculate the full available duration when none is supplied."""
        timeslot_without_duration = self.timeslot()
        timeslot_without_duration.pop("duration")

        for timeslot in [timeslot_without_duration, self.timeslot(duration="")]:
            with self.subTest(timeslot=timeslot):
                form = EventForm(
                    data=self.form_data(timeslots=json.dumps([timeslot]))
                )

                self.assertTrue(form.is_valid())
                self.assertEqual(form.cleaned_data["timeslots"][0]["duration"], 120)

    def test_timeslot_category_must_contain_non_whitespace_characters(self):
        """Reject missing, blank, whitespace-only, and non-string categories."""
        timeslot_without_category = self.timeslot()
        timeslot_without_category.pop("category")
        invalid_timeslots = [
            timeslot_without_category,
            self.timeslot(category=None),
            self.timeslot(category=""),
            self.timeslot(category="   "),
            self.timeslot(category=123),
        ]

        for timeslot in invalid_timeslots:
            with self.subTest(timeslot=timeslot):
                form = EventForm(
                    data=self.form_data(timeslots=json.dumps([timeslot]))
                )

                self.assertFalse(form.is_valid())
                self.assertIn("timeslots", form.errors)

    def test_invalid_json(self):
        """Reject malformed JSON in the timeslot field."""
        form = EventForm(data=self.form_data(timeslots="{broken"))

        self.assertFalse(form.is_valid())
        self.assertIn("timeslots", form.errors)

    def test_start_date_after_end_date(self):
        """Reject an event end date before its start date."""
        start_date = timezone.localdate() + timedelta(days=2)
        end_date = start_date - timedelta(days=1)
        form = EventForm(
            data=self.form_data(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)
