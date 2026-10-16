from django.shortcuts import redirect, render
from .models import Einreichung
from .forms import EinreichungForm
from veranstaltungen.models import Veranstaltung
from veranstaltungen.utils import get_event

def event_list(request):
    events = Veranstaltung.objects.all()
    context = {'events': events}
    return render(request,'einreichung/einreichung_list.html',context)

def event_bewerbung(request, event_id):
    if request.method == "POST":
        form = EinreichungForm(event_id=event_id, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("Basis:index")
    else:
        form = EinreichungForm(event_id=event_id)
    event = get_event(event_id)
    context = {'event': event, 'form': form}
    return render(request,'einreichung/bewerbung.html',context)
