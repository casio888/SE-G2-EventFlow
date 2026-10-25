import json
from datetime import time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, Timeslot


class EventCreateViewTests(TestCase):
    """Test the event creation view.

    Focus:
    - GET: The form is displayed correctly
    - POST: The event is persisted
    """

    def test_get_form(self):
        """Return the event form with the expected content."""
        response = self.client.get(reverse("events:event_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event anlegen")

    def test_post_creates_event(self):
        """Create an event and its valid timeslot from a POST request."""
        start_date = timezone.localdate() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        response = self.client.post(
            reverse("events:event_create"),
            {
                "title": "Test Event",
                "description": "Beschreibung",
                "location": "Frankfurt",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
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
            },
        )

        # Redirect after successful persistence.
        self.assertEqual(response.status_code, 302)

        # Exactly one event was created.
        self.assertEqual(Event.objects.count(), 1)

        event = Event.objects.first()
        self.assertEqual(event.title, "Test Event")

        # The timeslot was persisted correctly.
        self.assertEqual(event.timeslots.count(), 1)
        timeslot = event.timeslots.get()
        self.assertEqual(timeslot.start, time(10, 0))
        self.assertEqual(timeslot.end, time(12, 0))
        self.assertEqual(timeslot.duration, 120)
        self.assertEqual(timeslot.category, "Workshop")

    def test_post_does_not_persist_invalid_timeslot(self):
        """Do not persist an event when its timeslot fails validation."""
        start_date = timezone.localdate() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        response = self.client.post(
            reverse("events:event_create"),
            {
                "title": "Invalid Event",
                "description": "Description",
                "location": "Frankfurt",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "timeslots": json.dumps(
                    [
                        {
                            "start": "10:00",
                            "end": "12:00",
                            "duration": "121",
                            "category": "Workshop",
                        }
                    ]
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Timeslot.objects.count(), 0)
