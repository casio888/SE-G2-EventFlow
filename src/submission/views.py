from django.shortcuts import render
from .models import Einreichung
from events.models import Veranstaltung

def event_list(request):
    events=Veranstaltung.objects.all()
    context={'events': events}
    return render(request,'submission/submission.html',context)

def event_application(request):
    event=Veranstaltung.objects.all() #hier muss geändert werden, auf das gewollte Event
    context={'event':event}
    return render(request,'submission/application.html',context)
# Create your views here.
