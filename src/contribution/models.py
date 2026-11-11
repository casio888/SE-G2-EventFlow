from django.db import models
from events.models import Event
from authentication.models import CustomUserContributer

class Contribution(models.Model):
    """Model for a User contribution to an event. Requirements holds requests from the contributer
    accepted=true means the event has accepted this contribution.

    Returns:
        _type_: _description_
    """
    fk_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    fk_contributor = models.ForeignKey(CustomUserContributer, on_delete=models.CASCADE)
    accepted = models.BooleanField()
    duration_requested = models.PositiveIntegerField()
    description = models.TextField(max_length=400)
    requirements = models.TextField(max_length=400)

    def __str__(self):
        return "{self.id}: {fk_contributor.last_name} ({fk_contributor.id}) on Event: {fk_event.id}"
