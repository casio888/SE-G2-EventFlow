import json
from django.test import TestCase
from django.urls import reverse
from veranstaltungen.models import Veranstaltung

class VeranstaltungCreateViewTests(TestCase):

    def test_get_form(self):
        response = self.client.get(reverse("veranstaltung_erstellen"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Neue Veranstaltung erstellen")

    def test_post_creates_event(self):
        response = self.client.post(reverse("veranstaltung_erstellen"), {
            "titel": "Test Event",
            "beschreibung": "Beschreibung",
            "ort": "Frankfurt",
            "start_datum": "2026-02-23",
            "end_datum": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "ende": "12:00", "dauer": "120", "kategorie": "Workshop"}
            ])
        })

        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(Veranstaltung.objects.count(), 1)

        event = Veranstaltung.objects.first()
        self.assertEqual(event.titel, "Test Event")
        self.assertEqual(len(event.timeslots), 1)
