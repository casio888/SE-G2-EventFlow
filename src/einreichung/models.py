from django.db import models
from django.utils import timezone
from veranstaltungen.models import Veranstaltung

class Einreichung(models.Model):
    fk=models.ForeignKey(Veranstaltung, on_delete=models.CASCADE) 
    eingereicht=models.BooleanField(default=False)
    Beschreibung=models.CharField(max_length=400)
    Anforderungen=models.TextField(max_length=400)
    def __str__(self):
        return self.id
    def ist_in_zukunft(self):
        """Gibt True zurück, wenn die Veranstaltung in der Zukunft liegt"""
        return self.fk.start_datum >= timezone.now().date()
    def ist_in_vergangenheit(self):
        """Gibt True zurück, wenn die VEranstaltung in der Vergangenheiit liegt"""
        return self.fk.end_datum < timezone.now().date()
# Create your models here.
