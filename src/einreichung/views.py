from django.shortcuts import redirect, render
from .models import Einreichung
from .forms import EinreichungForm
from veranstaltungen.models import Veranstaltung
from veranstaltungen.utils import get_event

def event_list(request):
<<<<<<< HEAD
<<<<<<< HEAD
    events = Veranstaltung.objects.all()
    context = {'events': events}
    return render(request,'einreichung/einreichung_list.html', context)
=======
    events=Veranstaltung.objects.all()
    context={'events': events}
=======
    events = Veranstaltung.objects.all()
    context = {'events': events}
>>>>>>> 2230622 (wip: preparation for event application)
    return render(request,'einreichung/einreichung_list.html',context)
>>>>>>> 2ddd4b6 (refactor: renamed template for clearity going forward)

def event_bewerbung(request, event_id):
<<<<<<< HEAD
    # TODO Once users are implemented, throw error when einreichung existiert
    if request.method == "POST":
        form = EinreichungForm(event_id=event_id, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("Basis:index")
    else:
        form = EinreichungForm(event_id=event_id)
    event = get_event(event_id)
    context = {'event': event, 'form': form}
=======
    event = get_event(event_id)
    context = {'event':event}
>>>>>>> 2230622 (wip: preparation for event application)
    return render(request,'einreichung/bewerbung.html',context)
