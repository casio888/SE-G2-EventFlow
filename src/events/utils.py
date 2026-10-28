from .forms import EventForm

def get_event_form(request, event=None):
    if request.method == "POST":
        return EventForm(request.POST, instance=event)
    
    return EventForm(instance=event)

def save_event_form(form):
    if form.is_valid():
        return form.save()

    return None
