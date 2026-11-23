from .models import Contribution
from events.models import Event
from django.shortcuts import get_object_or_404, render

def get_contributions_for_event(event_id):
    """
    Retrieve all contributions submitted for a specific event.

    Arguments:
        event_id (int): The primary key of the event.

    Returns:
        QuerySet: All Contribution objects belonging to the event.
            The QuerySet is empty if no contributions exist.
    """
    return Contribution.objects.filter(fk_event__pk=event_id)
