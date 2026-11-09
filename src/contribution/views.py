from django.shortcuts import render, get_object_or_404
from .models import Contribution
from .utils import get_contributions_for_event
from events.models import Event

def event_list(request):
    events=Event.objects.all()
    context={'events': events}
    return render(request,'contribution/contribution.html',context)

def event_application(request):
    event=Event.objects.all() #hier muss geändert werden, auf das gewollte Event
    context={'event':event}
    return render(request,'contribution/application.html',context)
# Create your views here.

def event_contributions(request,event_id):
    """
    Display the contributions submitted for an event.

    Retrieves the event by its ID and loads all related contributions.
    If contributions exist, they are passed to the template. Otherwise,
    a message indicating that no submissions are available is shown.
    This view is intended for organizers.

    Arguments:
        request (HttpRequest): The HTTP request object.
        event_id (int): The primary key of the event.

    Returns:
        HttpResponse: The rendered contribution list page containing the
            event, its contributions or an informational message.
    """
    event= get_object_or_404(Event, pk=event_id)
    contribution_list=get_contributions_for_event(event_id)
    # checks if contributions does exist
    context={"event":event}
    if contribution_list.exists():
        context ['contributions']= contribution_list
    else:
        context ['message']="Keine Einreichungen vorhanden."

    return render(request,'contribution/contribution_list.html',context)
# Create your views here.