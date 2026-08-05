from django.utils import timezone
from django.shortcuts import render
from .models import Einreichung
from veranstaltungen.models import Veranstaltung

def event_list(request):
    events=Veranstaltung.objects.filter(end_datum__gt=timezone.now().date())
    context={'events': events}
    return render(request,'einreichung/einreichung.html',context)

def event_bewerbung(request):
    event=Veranstaltung.objects.all() #hier muss geändert werden, auf das gewollte Event
    context={'event':event}
    return render(request,'einreichung/bewerbung.html',context)
# Create your views here.
