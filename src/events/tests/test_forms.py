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
