from django.shortcuts import render
from .models import Contribution
from .utils import get_contributions_for_Event
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
    #function wich gives a site with the contributions for the chosen Event. (View for Organizer)
    try:
        event= Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return render(request, 'error.html',{'message':'Event konnte nicht gefunden werden'})
    contribution_list=get_contributions_of_event(event_id)
    # checks if contributions does exist
    if contribution_list.exists():
        contributions ['contribution']= contribution_list
    else:
        contributions ['message']="Keine Einreichungen vorhanden."

    return render(request,'contribution/contributionlist.html',event,contributions)
# Create your views here.