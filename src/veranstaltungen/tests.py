from datetime import date
from django.test import TestCase

from .models import Veranstaltung

# Create your tests here.

class VeranstaltungModelTests(TestCase):

    event_titel       = "A test Titel"
    event_beschreibung= "This is the description for the test event"
    event_datum_1     = date(2026, 6, 1)
    event_datum_2    = date(2026, 6, 2)
    event_ort         = "Dresden"

    def test_models_Veranstaltung_returns_title_als_str(self):
        event = Veranstaltung.objects.create(
                titel         = self.event_titel,
                beschreibung  = self.event_beschreibung,
                start_datum   = self.event_datum_1,
                end_datum     = self.event_datum_2,
                ort           = self.event_ort
                )
        self.assertEqual(str(event), self.event_titel)

