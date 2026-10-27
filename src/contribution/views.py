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

def table_of_contributions(request):
    # get the contributions of an Event and make list of it. List will be shown to organizer
    contributions=get_contributions_for_Event()
    context={'contribution':contributions}
    return render(request,'contribution/tableofcontributions.html',context)
