from .forms import VeranstaltungForm

def get_veranstaltung_form(request, event=None):
    if request.method == "POST":
        return VeranstaltungForm(request.POST, instance=event)
    
    return VeranstaltungForm(instance=event)

def save_veranstaltung_form(form):
    if form.is_valid():
        return form.save()

    return None
