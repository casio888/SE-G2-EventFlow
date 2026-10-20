from django.db import models
from events.models import Event

class Einreichung():
    fk=models.ForeignKey(Event, on_delete=models.CASCADE) 
    eingereicht=models.BooleanField()
    Beschreibung=models.CharField(max_length="400")
    Anforderungen=models.TextField(max_length="400")
    def __str__(self):
        return self.id
# Create your models here.
