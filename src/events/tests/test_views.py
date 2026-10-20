import json
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

    def test_post_creates_event(self):
        """
        Testet, dass eine gültige POST-Anfrage eine Veranstaltung erzeugt.
        """
        response = self.client.post(reverse("events:event_create"), {
            "title": "Test Event",
            "description": "Beschreibung",
            "location": "Frankfurt",
            "start_date": "2026-02-23",
            "end_date": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "end": "12:00", "duration": "120", "category": "Workshop"}
            ])
        })

        # Redirect nach erfolgreichem Speichern
        self.assertEqual(response.status_code, 302)

        # Es wurde genau ein Event angelegt
        self.assertEqual(Event.objects.count(), 1)

        event = Event.objects.first()
        self.assertEqual(event.title, "Test Event")

        # Timeslots wurden korrekt gespeichert
        self.assertEqual(event.timeslots.count(), 1)
