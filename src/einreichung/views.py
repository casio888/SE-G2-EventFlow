from django.shortcuts import render
from .models import Einreichung
from veranstaltungen.models import Veranstaltung
from veranstaltungen.utils import get_event

def event_list(request):
    events = Veranstaltung.objects.all()
    context = {'events': events}
    return render(request,'einreichung/einreichung_list.html',context)

def event_bewerbung(request, event_id):
    event = get_event(event_id)
    context = {'event':event}
    return render(request,'einreichung/bewerbung.html',context)
# Create your views here.
