import json
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from events.models import Event


class EventCreateViewTests(TestCase):
    """
    Testet die View zum Erstellen einer Veranstaltung.

    Fokus:
    - GET: Formular wird korrekt angezeigt
    - POST: Veranstaltung wird gespeichert
    """

    def test_get_form(self):
        """
        Testet, dass die Formularseite erreichbar ist
        und den erwarteten Inhalt enthält.
        """
        response = self.client.get(reverse("events:event_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event anlegen")

    @patch(
        "events.forms.timezone.localdate",
        return_value=date(2026, 10, 17),
    )
    def test_post_creates_event(self, _mock_localdate):
        """
        Testet, dass eine gültige POST-Anfrage eine Veranstaltung erzeugt.
        """
        response = self.client.post(
            reverse("events:event_create"),
            {
                "title": "Test Event",
                "description": "Beschreibung",
                "location": "Frankfurt",
                "start_date": "2026-10-17",
                "end_date": "2026-10-17",
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

        # Redirect nach erfolgreichem Speichern
        self.assertEqual(response.status_code, 302)

        # Es wurde genau ein Event angelegt
        self.assertEqual(Event.objects.count(), 1)

        event = Event.objects.first()
        self.assertEqual(event.title, "Test Event")

        # Timeslots wurden korrekt gespeichert
        self.assertEqual(event.timeslots.count(), 1)

    @patch(
        "events.forms.timezone.localdate",
        return_value=date(2026, 10, 17),
    )
    def test_post_rejects_past_start_date(self, _mock_localdate):
        """Reject an event whose start date is in the past."""
        response = self.client.post(
            reverse("events:event_create"),
            {
                "title": "Past Event",
                "description": "Beschreibung",
                "location": "Frankfurt",
                "start_date": "2026-10-16",
                "end_date": "2026-10-17",
                "timeslots": "[]",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)
        self.assertIn("start_date", response.context["form"].errors)
