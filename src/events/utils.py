from .forms import EventForm
from .models import Event

def get_event_form(request, event=None):
    if request.method == "POST":
        return EventForm(request.POST, instance=event)
    
    return EventForm(instance=event)

def save_event_form(form):
    if form.is_valid():
        return form.save()

def get_event(event_id):
    """Sanitize event request, because event_id is user supplied.

    Args:
        event_id (int): ID of a valid event 

    Returns:
        Event: Returns the corresponding Event, or None if input was wrong or id is not found
    """
    if (type(event_id) != type(int)):
        return None
    try: 
        return Event.objects.get(event_id=event_id)
    except:
        return None
