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

class Timeslot(models.Model):
    veranstaltung = models.ForeignKey(
        Veranstaltung,
        on_delete=models.CASCADE,
        related_name="timeslots"
    )
    start = models.TimeField()
    ende = models.TimeField()
    dauer = models.PositiveIntegerField()
    kategorie = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.start} - {self.ende} ({self.kategorie})"
