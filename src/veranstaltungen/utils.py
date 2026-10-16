from .forms import VeranstaltungForm
from .models import Veranstaltung

def get_veranstaltung_form(request, event=None):
    if request.method == "POST":
        return VeranstaltungForm(request.POST, instance=event)
    
    return VeranstaltungForm(instance=event)

def save_veranstaltung_form(form):
    if form.is_valid():
        return form.save()

    return None

def get_event(event_id):
    """Returns an Event with the requested ID. event_id is a user input and has to be validated. 
    For an Invalid id, return Null

    Args:
        event_id <Int>: Event id from the Database
    """
    if type(event_id) == int:
        # If element does not exist, event = Null
        event = Veranstaltung.objects.get(id=event_id)
        return event
    else:
        return Null