from django.db import models
from events.models import Event

class Contribution():
    """Model for a User contribution to an event. Requirements holds requests from the contributer
    accepted=true means the event has accepted this contribution.

    Returns:
        _type_: _description_
    """
    fk_event = models.ForeignKey(Veranstaltung, on_delete=models.CASCADE)
    accepted = models.BooleanField()
    duration_requested = models.PositiveIntegerField()
    description = models.TextField(max_length=400)
    requirements = models.TextField(max_length=400)

    def __str__(self):
        return self.id
