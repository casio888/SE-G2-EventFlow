from django.db import models

class Event_foreinreicher(models.Model):
    name=models.CharField(max_length=200)
    zeit=models.DateTimeField()
    ort= models.CharField(max_length=200)
    kategorien= models.CharField(max_length=200)
    maker=models.CharField(max_length=50,blank=True)

    def __str__(self):
        return self.name
# Create your models here.
