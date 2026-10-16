from django.db import models
from veranstaltungen.models import Veranstaltung

class Einreichung(models.Model):
    fk = models.ForeignKey(Veranstaltung, on_delete=models.CASCADE) 
    eingereicht = models.BooleanField()
    duration_requested = models.PositiveIntegerField()
    Beschreibung = models.CharField(max_length=400)
    Anforderungen = models.TextField(max_length=400)

    
