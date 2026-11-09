from django.db import models
from events.models import Event
from authentication.models import CustomUserContributer

class Contribution(models.Model):
    event=models.ForeignKey(Event, on_delete=models.CASCADE)
    contributer=models.ForeignKey(CustomUserContributer,on_delete=models.CASCADE)
    submitted=models.BooleanField()
    description=models.CharField(max_length=400)
    requirements=models.TextField(max_length=400)
    def __str__(self):
        return self.id
# Create your models here.
