from django.shortcuts import render
from .models import Contribution
from .forms import ContributionForm
from events.models import Event
from events.utils import get_event

def event_list(request):
    """Shows a List of all Events and Buttons to start submitting a contribution
    Temporary, will be replaced bby Submit buttons on start and event detail pages and search

    Args:
        request <request>: URL Request

    Returns:
        <HTML>: Rendered website
    """
    events=Event.objects.all()
    context={'events': events}
    return render(request,'contribution/contribution.html',context)

def event_application(request, event_id):
    """Opens a Form to submit a new contribution to an event.
    TODO Should refuse to open and redirect back, once user roles are implemented, and an application for an event already exists

    Args:
        request <request>: URL Request
        event_id <int>: Valid ID of an Event

    Returns:
        <HTML>: Rendered Website
    """
    # TODO Once users are implemented, throw error when einreichung existiert
    if request.method == "POST":
        form = ContributionForm(event_id=event_id, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("base:index")
    else:
        form = ContributionForm(event_id=event_id)
    event = get_event(event_id)
    context = {'event': event, 'form': form}
    return render(request,'contribution/application.html',context)