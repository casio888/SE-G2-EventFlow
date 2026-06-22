import datetime

from django.test import TestCase
from django.utils import timezone
#from django.urls import reverse
from .models import Einreichung
from veranstaltungen.models import Veranstaltung

class QuestionModelTests(TestCase):
    # Soll nicht anzeigen, was in der Vergangenheit liegt
    def test_event_in_past(self):
        """Gibt True zurück, wenn die Veranstaltung vorbei ist"""
        past_date= (timezone.now()- datetime.timedelta(days=1)).date()

        veranstaltung=Veranstaltung.objects.create(
            titel="Test event",
            start_datum=past_date-datetime.timedelta(days=1),
            end_datum=past_date,
            ort="Test Ort"
        )
        past_event=Einreichung(fk=veranstaltung)
        self.assertTrue(past_event.ist_in_vergangenheit())

    # Soll anzeigen, was noch ist
    def test_is_in_future(self):
        """Gibt True zurück, wenn die Veranstaltung ab Heute ist."""
        future_date= (timezone.now()).date()
        veranstaltung=Veranstaltung.objects.create(
            titel="Test event",
            start_datum=future_date,
            end_datum=future_date+datetime.timedelta(days=1),
            ort="Test Ort"
        )
        future_event=Einreichung(fk=veranstaltung)
        self.assertTrue(future_event.ist_in_zukunft())

# Create your tests here.