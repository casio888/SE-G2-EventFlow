import json
from datetime import date
from unittest.mock import patch

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

    @patch(
        "veranstaltungen.forms.timezone.localdate",
        return_value=date(2026, 10, 17),
    )
    def test_post_creates_event(self, _mock_localdate):
        """
        Testet, dass eine gültige POST-Anfrage eine Veranstaltung erzeugt.
        """
        response = self.client.post(
            reverse("veranstaltungen:veranstaltung_erstellen"),
            {
                "titel": "Test Event",
                "beschreibung": "Beschreibung",
                "ort": "Frankfurt",
                "start_datum": "2026-10-18",
                "end_datum": "2026-10-19",
                "timeslots": json.dumps(
                    [
                        {
                            "start": "10:00",
                            "ende": "12:00",
                            "dauer": "120",
                            "kategorie": "Workshop",
                        }
                    ]
                ),
            },
        )

        # Redirect nach erfolgreichem Speichern
        self.assertEqual(response.status_code, 302)

        # Es wurde genau ein Event angelegt
        self.assertEqual(Veranstaltung.objects.count(), 1)

        event = Veranstaltung.objects.first()
        self.assertEqual(event.titel, "Test Event")

        # Timeslots wurden korrekt gespeichert
        self.assertEqual(event.timeslots.count(), 1)
