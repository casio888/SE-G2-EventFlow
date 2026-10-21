from django.shortcuts import render
from .models import Submission
from events.models import Event

def event_list(request):
    events=Event.objects.all()
    context={'events': events}
    return render(request,'submission/submission.html',context)

def event_application(request):
    event=Event.objects.all() #hier muss geändert werden, auf das gewollte Event
    context={'event':event}
    return render(request,'submission/application.html',context)
# Create your views here.
