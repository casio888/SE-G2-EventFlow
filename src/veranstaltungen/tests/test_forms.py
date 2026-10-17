import json
from datetime import date
from unittest.mock import patch

from django.test import TestCase

from veranstaltungen.forms import VeranstaltungForm
from veranstaltungen.models import Veranstaltung


FIXED_TODAY = date(2026, 10, 17)


class VeranstaltungFormTests(TestCase):
    """
    Testet die Validierung des VeranstaltungFormulars.

    Fokus:
    - Validierung der Timeslot-Daten
    - Validierung der Veranstaltungsdaten
    - Fehlerfälle bei Zeitformat, Dauer und Kategorie
    """

    def setUp(self):
        self.localdate_patcher = patch(
            "veranstaltungen.forms.timezone.localdate",
            return_value=FIXED_TODAY,
        )
        self.localdate_patcher.start()
        self.addCleanup(self.localdate_patcher.stop)

    @staticmethod
    def form_data(**overrides) -> dict:
        """Erstellt gültige Formulardaten für einen Testfall."""
        data = {
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
        }
        data.update(overrides)
        return data

    def test_single_day_event_is_valid(self):
        """
        Testet, ob ein gültiges eintägiges Event angelegt werden kann.
        """
        form = VeranstaltungForm(
            data=self.form_data(
                start_datum="2026-10-17",
                end_datum="2026-10-17",
            )
        )

        self.assertTrue(form.is_valid())

    def test_start_date_in_past_is_invalid(self):
        """Testet, dass neue Events nicht in der Vergangenheit beginnen."""
        form = VeranstaltungForm(
            data=self.form_data(
                start_datum="2026-10-16",
                end_datum="2026-10-18",
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("start_datum", form.errors)

    def test_five_calendar_year_limit_including_leap_day(self):
        """Testet die inklusive Fünfjahresgrenze ab einem 29. Februar."""
        with patch(
            "veranstaltungen.forms.timezone.localdate",
            return_value=date(2028, 2, 29),
        ):
            form_at_limit = VeranstaltungForm(
                data=self.form_data(
                    start_datum="2033-02-28",
                    end_datum="2033-02-28",
                )
            )
            form_after_limit = VeranstaltungForm(
                data=self.form_data(
                    start_datum="2033-02-28",
                    end_datum="2033-03-01",
                )
            )
            form_with_late_start = VeranstaltungForm(
                data=self.form_data(
                    start_datum="2033-03-01",
                    end_datum="2033-03-01",
                )
            )

            self.assertTrue(form_at_limit.is_valid())
            self.assertFalse(form_after_limit.is_valid())
            self.assertIn("end_datum", form_after_limit.errors)
            self.assertFalse(form_with_late_start.is_valid())
            self.assertIn("start_datum", form_with_late_start.errors)

    def test_existing_past_start_date_may_remain_unchanged(self):
        """Testet ein unverändertes vergangenes Startdatum beim Bearbeiten."""
        event = Veranstaltung.objects.create(
            titel="Bestehendes Event",
            beschreibung="Beschreibung",
            ort="Frankfurt",
            start_datum=date(2026, 10, 15),
            end_datum=date(2026, 10, 16),
        )
        form = VeranstaltungForm(
            instance=event,
            data=self.form_data(
                start_datum="2026-10-15",
                end_datum="2026-10-16",
            ),
        )
        form_with_changed_start = VeranstaltungForm(
            instance=event,
            data=self.form_data(
                start_datum="2026-10-14",
                end_datum="2026-10-16",
            ),
        )

        self.assertTrue(form.is_valid())
        self.assertFalse(form_with_changed_start.is_valid())
        self.assertIn("start_datum", form_with_changed_start.errors)

    def test_timeslot_start_after_end(self):
        """
        Testet, dass ein Timeslot ungültig ist,
        wenn die Startzeit nach der Endzeit liegt.
        """
        form = VeranstaltungForm(
            data=self.form_data(
                timeslots=json.dumps(
                    [
                        {
                            "start": "14:00",
                            "ende": "12:00",
                            "dauer": "120",
                            "kategorie": "Workshop",
                        }
                    ]
                )
            )
        )
        self.assertFalse(form.is_valid())

    def test_timeslot_missing_category(self):
        """
        Testet, dass ein Timeslot ungültig ist,
        wenn die Kategorie fehlt.
        """
        form = VeranstaltungForm(
            data=self.form_data(
                timeslots=json.dumps(
                    [
                        {
                            "start": "10:00",
                            "ende": "12:00",
                            "dauer": "120",
                            "kategorie": "",
                        }
                    ]
                )
            )
        )
        self.assertFalse(form.is_valid())

    def test_timeslot_invalid_duration(self):
        """
        Testet, dass eine negative Dauer abgelehnt wird.
        """
        form = VeranstaltungForm(
            data=self.form_data(
                timeslots=json.dumps(
                    [
                        {
                            "start": "10:00",
                            "ende": "12:00",
                            "dauer": "-5",
                            "kategorie": "Workshop",
                        }
                    ]
                )
            )
        )
        self.assertFalse(form.is_valid())

    def test_invalid_json(self):
        """
        Testet, dass ungültiges JSON im Timeslot-Feld
        korrekt abgefangen wird.
        """
        form = VeranstaltungForm(data=self.form_data(timeslots="{kaputt"))
        self.assertFalse(form.is_valid())

    def test_start_date_after_end_date(self):
        """
        Testet, dass das Startdatum nicht nach dem Enddatum liegen darf.
        """
        form = VeranstaltungForm(
            data=self.form_data(
                start_datum="2026-10-19",
                end_datum="2026-10-18",
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_datum", form.errors)
