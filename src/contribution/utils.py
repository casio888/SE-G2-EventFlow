from .models import Contribution
from events.models import Event
from django.shortcuts import get_object_or_404, render

def get_contributions_for_event(event_id):
    """Uses the Event and search for contributions for this Event
     Uses Databases

     """
    return Contribution.objects.filter(event_id=event_id)
