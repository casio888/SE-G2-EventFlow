from .models import Contribution
from events.models import Event
from django.shortcuts import get_object_or_404, render

def get_contributions_for_event(event_id):
    """
    Retrieve all contributions submitted for a specific event.

    Queries the database for all Contribution objects whose event_id
    matches the given event. The result is a QuerySet, which can be
    evaluated lazily or checked with exists().

    Arguments:
        event_id (int): The primary key of the event.

    Returns:
        QuerySet: All Contribution objects belonging to the event.
            The QuerySet is empty if no contributions exist.
    """
    return Contribution.objects.filter(event_id=event_id)
