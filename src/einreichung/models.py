from django.db import models
from veranstaltungen.models import Veranstaltung

class Einreichung():
    fk=models.ForeignKey(Veranstaltung, on_delete=models.CASCADE) 
    eingereicht=models.BooleanField()
    Beschreibung=models.CharField(max_length="400")
    Anforderungen=models.TextField(max_length="400")
    def __str__(self):
        return self.id
# Create your models here.
