from django.db import models
from events.models import Event

class Contribution():
    event=models.ForeignKey(Event, on_delete=models.CASCADE) 
    submitted=models.BooleanField()
    description=models.CharField(max_length="400")
    requirements=models.TextField(max_length="400")
    def __str__(self):
        return self.id
# Create your models here.
