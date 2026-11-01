from django.db import models

class Event(models.Model):
    """
    Repräsentiert eine Veranstaltung im System.

    Attributes:
        title (str): Titel der Veranstaltung
        description (str): Beschreibung / Catchphrase
        start_date (date): Startdatum
        end_date (date): Enddatum
        location (str): Veranstaltungsort
        created_at (datetime): Automatisch gesetztes Erstellungsdatum
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Timeslot(models.Model):
    """A scheduled timeslot belonging to an event.

    Attributes:
        event (FK): Event containing the timeslot
        start (time): Start time
        end (time): End time
        duration (int): Duration in minutes
        category (str): Timeslot category
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="timeslots"
    )
    start = models.TimeField()
    end = models.TimeField()
    duration = models.PositiveIntegerField()
    category = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.start} - {self.end} ({self.category})"
