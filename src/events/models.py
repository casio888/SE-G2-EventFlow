from django.db import models

class Veranstaltung(models.Model):
    """
    Repräsentiert eine Veranstaltung im System.

    Attributes:
        titel (str): Titel der Veranstaltung
        beschreibung (str): Beschreibung / Catchphrase
        start_datum (date): Startdatum
        end_datum (date): Enddatum
        ort (str): Veranstaltungsort
        erstellt_am (datetime): Automatisch gesetztes Erstellungsdatum
    """
    titel = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True)
    start_datum = models.DateField()
    end_datum = models.DateField()
    ort = models.CharField(max_length=200) 
    erstellt_am = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titel

class Timeslot(models.Model):
    """
    Einzelner Timeslot einer Veranstaltung.

    Attributes:
        veranstaltung (FK): Zugehörige Veranstaltung
        start (time): Startzeit
        ende (time): Endzeit
        dauer (int): Dauer in Minuten
        kategorie (str): Kategorie des Timeslots
    """
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
