from datetime import date

from django.test import TestCase

from einreichung.forms import EinreichungForm
from veranstaltungen.models import Veranstaltung


class EinreichungFormTests(TestCase):
    def setUp(self):
        self.veranstaltung = Veranstaltung.objects.create(
            titel="Testveranstaltung",
            beschreibung="",
            start_datum=date(2026, 10, 16),
            end_datum=date(2026, 10, 17),
            ort="Dresden",
        )

    def test_status_is_defaulted_and_not_exposed(self):
        form = EinreichungForm(event_id=self.veranstaltung.pk)

        self.assertNotIn("eingereicht", form.fields)
        self.assertNotIn("fk", form.fields)
        self.assertFalse(form.instance.eingereicht)
        self.assertEqual(form.instance.fk, self.veranstaltung)

    def test_save_sets_venue_and_keeps_status_false(self):
        form = EinreichungForm(
            data={
                "duration_requested": "30",
                "Beschreibung": "Ein Beitrag",
                "Anforderungen": "Beamer",
                "eingereicht": "on",
            },
            event_id=self.veranstaltung.pk,
        )

        self.assertTrue(form.is_valid(), form.errors)
        einreichung = form.save()

        self.assertEqual(einreichung.fk, self.veranstaltung)
        self.assertFalse(einreichung.eingereicht)
