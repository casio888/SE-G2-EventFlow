import json
from django.test import TestCase
from veranstaltungen.forms import VeranstaltungForm

class VeranstaltungFormTests(TestCase):

    def test_form_valid(self):
        form = VeranstaltungForm(data={
            "titel": "Test Event",
            "beschreibung": "Beschreibung",
            "ort": "Frankfurt",
            "start_datum": "2026-02-23",
            "end_datum": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "ende": "12:00", "dauer": "120", "kategorie": "Workshop"}
            ])
        })
        self.assertTrue(form.is_valid())

    def test_timeslot_start_after_end(self):
        form = VeranstaltungForm(data={
            "titel": "Test",
            "beschreibung": "",
            "ort": "Ort",
            "start_datum": "2026-02-23",
            "end_datum": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "14:00", "ende": "12:00", "dauer": "120", "kategorie": "Workshop"}
            ])
        })
        self.assertFalse(form.is_valid())

    def test_timeslot_missing_category(self):
        form = VeranstaltungForm(data={
            "titel": "Test",
            "beschreibung": "",
            "ort": "Ort",
            "start_datum": "2026-02-23",
            "end_datum": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "ende": "12:00", "dauer": "120", "kategorie": ""}
            ])
        })
        self.assertFalse(form.is_valid())

    def test_timeslot_invalid_duration(self):
        form = VeranstaltungForm(data={
            "titel": "Test",
            "beschreibung": "",
            "ort": "Ort",
            "start_datum": "2026-02-23",
            "end_datum": "2026-02-24",
            "timeslots": json.dumps([
                {"start": "10:00", "ende": "12:00", "dauer": "-5", "kategorie": "Workshop"}
            ])
        })
        self.assertFalse(form.is_valid())

    def test_invalid_json(self):
        form = VeranstaltungForm(data={
            "titel": "Test",
            "beschreibung": "",
            "ort": "Ort",
            "start_datum": "2026-02-23",
            "end_datum": "2026-02-24",
            "timeslots": "{kaputt"
        })
        self.assertFalse(form.is_valid())
