from .forms import VeranstaltungForm
from veranstaltungen.models import Veranstaltung
from django.utils import timezone

def get_veranstaltung_form(request, event=None):
    if request.method == "POST":
        return VeranstaltungForm(request.POST, instance=event)
    
    return VeranstaltungForm(instance=event)

def save_veranstaltung_form(form):
    if form.is_valid():
        return form.save()

    return None

def get_six_elements():

    event_list=list(Veranstaltung.objects
    .filter(start_datum__gt=timezone.now())
    .order_by('start_datum')[:6]
)  # get max 6 elements of Events and make list
    empty_event = {
        'titel': 'Demo',
        'beschreibung': 'Es fehlen Events',
        'start_datum': None,
        'end_datum': None,
        'ort': 'Hinterkleinsiestdenicht',
        }
    
    while len(event_list)< 6:
        event_list.append(empty_event)

    return event_list

    