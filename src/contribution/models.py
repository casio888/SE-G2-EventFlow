from django.db import models
from events.models import Event
from authentication.models import CustomUserContributer


class Contribution(models.Model):
    """Represent an application submitted by a contributor for an event.

    The status records the organizer's decision as one unambiguous value.
    New applications remain pending until an organizer accepts or rejects them.

    Attributes:
        fk_event (Event): Event receiving the application.
        fk_contributor (CustomUserContributer): User submitting the application.
        status (str): Current application status.
        duration_requested (int): Requested duration in minutes.
        description (str): Description of the proposed contribution.
        requirements (str): Resources required for the contribution.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Offen"
        ACCEPTED = "accepted", "Angenommen"
        REJECTED = "rejected", "Abgelehnt"

    fk_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    fk_contributor = models.ForeignKey(CustomUserContributer, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    duration_requested = models.PositiveIntegerField()
    description = models.TextField(max_length=400)
    requirements = models.TextField(max_length=400)

    def __str__(self):
        return f"{self.id}: User {self.fk_contributor.last_name} ({self.fk_contributor.id}) on Event: {self.fk_event.id}"
