import json
from django.test import TestCase
from events.forms import EventForm

class EventFormTests(TestCase):
    """
    Testet die Validierung des VeranstaltungFormulars.

    Fokus:
    - Validierung der Timeslot-Daten
    - Fehlerfälle bei Zeitformat, Dauer und Kategorie
    """

    def test_form_valid(self):
        """
        Testet, ob ein korrekt ausgefülltes Formular gültig ist.
        """
        form = EventForm(data={
            "title": "Test Event",
            "description": "Beschreibung",
            "location": "Frankfurt",
            "start_date": "2026-02-23",
            "end_date": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "end": "12:00", "duration": "120", "category": "Workshop"}
            ])
        })
        self.assertTrue(form.is_valid())

    def test_timeslot_start_after_end(self):
        """
        Testet, dass ein Timeslot ungültig ist,
        wenn die Startzeit nach der Endzeit liegt.
        """
        form = EventForm(data={
            "title": "Test",
            "description": "",
            "location": "Ort",
            "start_date": "2026-02-23",
            "end_date": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "14:00", "end": "12:00", "duration": "120", "category": "Workshop"}
            ])
        })
        self.assertFalse(form.is_valid())

    def test_timeslot_missing_category(self):
        """
        Testet, dass ein Timeslot ungültig ist,
        wenn die Kategorie fehlt.
        """
        form = EventForm(data={
            "title": "Test",
            "description": "",
            "location": "Ort",
            "start_date": "2026-02-23",
            "end_date": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "end": "12:00", "duration": "120", "category": ""}
            ])
        })
        self.assertFalse(form.is_valid())

    def test_timeslot_invalid_duration(self):
        """
        Testet, dass eine negative Dauer abgelehnt wird.
        """
        form = EventForm(data={
            "title": "Test",
            "description": "",
            "location": "Ort",
            "start_date": "2026-02-23",
            "end_date": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "end": "12:00", "duration": "-5", "category": "Workshop"}
            ])
        })
        self.assertFalse(form.is_valid())

    def test_invalid_json(self):
        """
        Testet, dass ungültiges JSON im Timeslot-Feld
        korrekt abgefangen wird.
        """
        form = EventForm(data={
            "title": "Test",
            "description": "",
            "location": "Ort",
            "start_date": "2026-02-23",
            "end_date": "2026-02-24",
            "timeslots": "{kaputt"
        })
        self.assertFalse(form.is_valid())

    def test_start_date_after_end_date(self):
        """
        Testet, dass das Startdatum nicht nach dem Enddatum liegen darf.
        """
        form = EventForm(data={
            "title": "Test",
            "description": "",
            "location": "Ort",
            "start_date": "2026-02-25",
            "end_date": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "end": "12:00", "duration": "120", "category": "Workshop"}
            ])
        })
        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)
