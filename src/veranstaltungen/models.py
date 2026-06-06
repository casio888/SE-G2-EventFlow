from django.db import models

class Veranstaltung(models.Model):
    titel = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True)
    start_datum = models.DateField()
    end_datum = models.DateField()
    ort = models.CharField(max_length=200)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titel
