from datetime import time, timedelta
from unittest.mock import patch

from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, Timeslot


def event_form_data(**overrides) -> dict:
    """Create valid event data for a view test."""
    event_date = (timezone.localdate() + timedelta(days=1)).isoformat()
    data = {
        "title": "Test Event",
        "description": "Description",
        "location": "Frankfurt",
        "start_date": event_date,
        "end_date": event_date,
    }
    data.update(overrides)
    return data


def timeslot_formset_data(slots=None, initial_forms=0) -> dict:
    """Create formset management data and indexed timeslot fields."""
    slots = slots or []
    data = {
        "timeslots-TOTAL_FORMS": str(len(slots)),
        "timeslots-INITIAL_FORMS": str(initial_forms),
        "timeslots-MIN_NUM_FORMS": "0",
        "timeslots-MAX_NUM_FORMS": "1000",
    }

    for index, slot in enumerate(slots):
        for field_name, value in slot.items():
            data[f"timeslots-{index}-{field_name}"] = value

    return data


def combined_form_data(slots=None, initial_forms=0, **event_overrides) -> dict:
    """Combine event fields with the related timeslot formset data."""
    data = event_form_data(**event_overrides)
    data.update(timeslot_formset_data(slots, initial_forms))
    return data


class EventCreateViewTests(TestCase):
    """Test combined event and timeslot creation."""

    def test_get_returns_event_form_and_timeslot_formset(self):
        """Provide both forms required by the combined create page."""
        response = self.client.get(reverse("events:event_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event anlegen")
        self.assertIn("form", response.context)
        self.assertIn("timeslot_formset", response.context)
        self.assertEqual(response.context["timeslot_formset"].prefix, "timeslots")

    def test_post_creates_event_without_timeslots(self):
        """Create an event when the optional formset is empty."""
        response = self.client.post(
            reverse("events:event_create"),
            combined_form_data(),
        )

        self.assertRedirects(response, reverse("events:events_your_events"))
        event = Event.objects.get()
        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.timeslots.count(), 0)

    def test_post_creates_event_with_multiple_timeslots(self):
        """Create multiple valid timeslots with calculated durations."""
        response = self.client.post(
            reverse("events:event_create"),
            combined_form_data(
                [
                    {
                        "category": "Workshop",
                        "start": "10:00",
                        "end": "12:00",
                    },
                    {
                        "category": "Panel",
                        "start": "13:15",
                        "end": "14:00",
                    },
                ]
            ),
        )

        self.assertRedirects(response, reverse("events:events_your_events"))
        event = Event.objects.get()
        timeslots = list(event.timeslots.order_by("start"))
        self.assertEqual(len(timeslots), 2)
        self.assertEqual(timeslots[0].category, "Workshop")
        self.assertEqual(timeslots[0].duration, 120)
        self.assertEqual(timeslots[1].category, "Panel")
        self.assertEqual(timeslots[1].duration, 45)

    def test_post_rejects_past_start_date(self):
        """Reject an event whose start date is in the past."""
        response = self.client.post(
            reverse("events:event_create"),
            combined_form_data(
                start_date=(
                    timezone.localdate() - timedelta(days=1)
                ).isoformat(),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)
        self.assertIn("start_date", response.context["form"].errors)

    def test_invalid_timeslot_prevents_event_creation(self):
        """Reject the complete submission when a timeslot is invalid."""
        response = self.client.post(
            reverse("events:event_create"),
            combined_form_data(
                [
                    {
                        "category": "Workshop",
                        "start": "10:00",
                        "end": "10:00",
                    }
                ]
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Timeslot.objects.count(), 0)
        self.assertIn("end", response.context["timeslot_formset"].forms[0].errors)

    def test_database_error_rolls_back_event_and_timeslots(self):
        """Roll back the event if saving a related timeslot fails."""
        data = combined_form_data(
            [{"category": "Workshop", "start": "10:00", "end": "11:00"}]
        )

        with patch(
            "events.forms.TimeslotForm.save",
            side_effect=DatabaseError("Database failure"),
        ):
            with self.assertRaises(DatabaseError):
                self.client.post(reverse("events:event_create"), data)

        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Timeslot.objects.count(), 0)


class EventEditViewTests(TestCase):
    """Test combined updates to events and their timeslots."""

    def setUp(self):
        event_date = timezone.localdate() + timedelta(days=1)
        self.event = Event.objects.create(
            title="Existing Event",
            description="Original description",
            location="Frankfurt",
            start_date=event_date,
            end_date=event_date,
        )
        self.timeslot = Timeslot.objects.create(
            event=self.event,
            category="Workshop",
            start=time(9, 0),
            end=time(10, 0),
            duration=60,
        )

    def edit_url(self) -> str:
        """Return the combined event edit URL."""
        return reverse("events:event_edit", args=[self.event.pk])

    def test_get_loads_existing_timeslots_ordered_by_start(self):
        """Load existing timeslots in start-time order for editing."""
        earlier_timeslot = Timeslot.objects.create(
            event=self.event,
            category="Opening",
            start=time(8, 0),
            end=time(8, 30),
            duration=30,
        )

        response = self.client.get(self.edit_url())

        self.assertEqual(response.status_code, 200)
        formset = response.context["timeslot_formset"]
        self.assertEqual(
            [form.instance.pk for form in formset.initial_forms],
            [earlier_timeslot.pk, self.timeslot.pk],
        )

    def test_post_updates_event_and_existing_timeslot_together(self):
        """Update parent and child fields in one submission."""
        response = self.client.post(
            self.edit_url(),
            combined_form_data(
                [
                    {
                        "id": str(self.timeslot.pk),
                        "category": "Panel",
                        "start": "11:00",
                        "end": "12:45",
                    }
                ],
                initial_forms=1,
                title="Updated Event",
            ),
        )

        self.assertRedirects(
            response,
            reverse("events:event_detail", args=[self.event.pk]),
        )
        self.event.refresh_from_db()
        self.timeslot.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Event")
        self.assertEqual(self.timeslot.category, "Panel")
        self.assertEqual(self.timeslot.start, time(11, 0))
        self.assertEqual(self.timeslot.end, time(12, 45))
        self.assertEqual(self.timeslot.duration, 105)

    def test_post_adds_multiple_timeslots_while_editing(self):
        """Add multiple new timeslots without duplicating an existing one."""
        response = self.client.post(
            self.edit_url(),
            combined_form_data(
                [
                    {
                        "id": str(self.timeslot.pk),
                        "category": "Workshop",
                        "start": "09:00",
                        "end": "10:00",
                    },
                    {
                        "category": "Talk",
                        "start": "10:30",
                        "end": "11:00",
                    },
                    {
                        "category": "Panel",
                        "start": "12:00",
                        "end": "13:15",
                    },
                ],
                initial_forms=1,
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.event.timeslots.count(), 3)
        self.assertTrue(
            self.event.timeslots.filter(pk=self.timeslot.pk).exists()
        )
        self.assertEqual(
            list(
                self.event.timeslots.order_by("start").values_list(
                    "duration", flat=True
                )
            ),
            [60, 30, 75],
        )

    def test_omitted_timeslots_are_preserved(self):
        """Do not treat omission from a submission as deletion."""
        omitted_timeslot = Timeslot.objects.create(
            event=self.event,
            category="Omitted",
            start=time(14, 0),
            end=time(15, 0),
            duration=60,
        )
        response = self.client.post(
            self.edit_url(),
            combined_form_data(
                [
                    {
                        "id": str(self.timeslot.pk),
                        "category": "Updated Workshop",
                        "start": "10:00",
                        "end": "11:00",
                    }
                ],
                initial_forms=1,
                title="Updated With Partial Timeslots",
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.timeslot.refresh_from_db()
        omitted_timeslot.refresh_from_db()
        self.assertEqual(self.event.title, "Updated With Partial Timeslots")
        self.assertEqual(self.timeslot.category, "Updated Workshop")
        self.assertEqual(self.timeslot.duration, 60)
        self.assertEqual(omitted_timeslot.category, "Omitted")
        self.assertEqual(omitted_timeslot.start, time(14, 0))

    def test_timeslot_id_from_another_event_cannot_modify_foreign_timeslot(self):
        """Keep a foreign timeslot unchanged when its ID is submitted."""
        other_event = Event.objects.create(
            title="Other Event",
            description="Description",
            location="Dresden",
            start_date=self.event.start_date,
            end_date=self.event.end_date,
        )
        foreign_timeslot = Timeslot.objects.create(
            event=other_event,
            category="Foreign",
            start=time(14, 0),
            end=time(15, 0),
            duration=60,
        )

        response = self.client.post(
            self.edit_url(),
            combined_form_data(
                [
                    {
                        "id": str(foreign_timeslot.pk),
                        "category": "Changed",
                        "start": "15:00",
                        "end": "16:00",
                    }
                ],
                initial_forms=1,
                title="Updated Event",
            ),
        )

        self.assertRedirects(
            response,
            reverse("events:event_detail", args=[self.event.pk]),
        )
        self.event.refresh_from_db()
        self.timeslot.refresh_from_db()
        foreign_timeslot.refresh_from_db()
        self.assertEqual(self.event.title, "Updated Event")
        self.assertEqual(self.timeslot.category, "Workshop")
        self.assertEqual(foreign_timeslot.category, "Foreign")
        self.assertEqual(foreign_timeslot.start, time(14, 0))
        self.assertEqual(foreign_timeslot.end, time(15, 0))
        self.assertEqual(foreign_timeslot.duration, 60)

    def test_invalid_event_prevents_timeslot_update(self):
        """Leave timeslots unchanged when the event form is invalid."""
        response = self.client.post(
            self.edit_url(),
            combined_form_data(
                [
                    {
                        "id": str(self.timeslot.pk),
                        "category": "Changed",
                        "start": "10:00",
                        "end": "11:00",
                    }
                ],
                initial_forms=1,
                title="",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.context["form"].errors)
        self.timeslot.refresh_from_db()
        self.assertEqual(self.timeslot.category, "Workshop")
        self.assertEqual(self.timeslot.start, time(9, 0))

    def test_invalid_timeslot_prevents_event_update(self):
        """Leave the event unchanged when a timeslot form is invalid."""
        response = self.client.post(
            self.edit_url(),
            combined_form_data(
                [
                    {
                        "id": str(self.timeslot.pk),
                        "category": "Changed",
                        "start": "11:00",
                        "end": "10:00",
                    }
                ],
                initial_forms=1,
                title="Must Not Change",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("end", response.context["timeslot_formset"].forms[0].errors)
        self.event.refresh_from_db()
        self.timeslot.refresh_from_db()
        self.assertEqual(self.event.title, "Existing Event")
        self.assertEqual(self.timeslot.category, "Workshop")


class EventDetailViewTests(TestCase):
    """Test event detail retrieval."""

    def setUp(self):
        event_date = timezone.localdate() + timedelta(days=1)
        self.event = Event.objects.create(
            title="Managed Event",
            description="Description",
            location="Frankfurt",
            start_date=event_date,
            end_date=event_date,
        )

    def create_timeslot(self, **overrides) -> Timeslot:
        """Create a stored timeslot for the managed event."""
        data = {
            "event": self.event,
            "start": time(9, 0),
            "end": time(10, 0),
            "duration": 60,
            "category": "Workshop",
        }
        data.update(overrides)
        return Timeslot.objects.create(**data)

    def test_event_detail_returns_timeslots_ordered_by_start(self):
        """Return only the event's timeslots ordered by start time."""
        later_timeslot = self.create_timeslot(
            category="Later Session",
            start=time(11, 0),
            end=time(12, 0),
        )
        earlier_timeslot = self.create_timeslot(
            category="Earlier Session",
            start=time(8, 0),
            end=time(9, 0),
        )
        other_event = Event.objects.create(
            title="Other Event",
            description="Description",
            location="Dresden",
            start_date=self.event.start_date,
            end_date=self.event.end_date,
        )
        Timeslot.objects.create(
            event=other_event,
            start=time(7, 0),
            end=time(8, 0),
            duration=60,
            category="Workshop",
        )

        response = self.client.get(
            reverse("events:event_detail", args=[self.event.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["timeslots"]),
            [earlier_timeslot, later_timeslot],
        )
