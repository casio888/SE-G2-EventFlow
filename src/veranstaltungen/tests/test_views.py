import json
from django.test import TestCase
from django.urls import reverse
from veranstaltungen.models import Veranstaltung

class VeranstaltungCreateViewTests(TestCase):
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
        response = self.client.get(reverse("veranstaltungen:veranstaltung_erstellen"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event anlegen")

    def test_post_creates_event(self):
        """
        Testet, dass eine gültige POST-Anfrage eine Veranstaltung erzeugt.
        """
        response = self.client.post(reverse("veranstaltungen:veranstaltung_erstellen"), {
            "titel": "Test Event",
            "beschreibung": "Beschreibung",
            "ort": "Frankfurt",
            "start_datum": "2026-02-23",
            "end_datum": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "ende": "12:00", "dauer": "120", "kategorie": "Workshop"}
            ])
        })

        # Redirect nach erfolgreichem Speichern
        self.assertEqual(response.status_code, 302)

        # Es wurde genau ein Event angelegt
        self.assertEqual(Veranstaltung.objects.count(), 1)

        event = Veranstaltung.objects.first()
        self.assertEqual(event.titel, "Test Event")

        # Timeslots wurden korrekt gespeichert
        self.assertEqual(event.timeslots.count(), 1)
