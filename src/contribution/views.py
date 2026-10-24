from django.shortcuts import render
from .models import Contribution
from .forms import ContributionForm
from events.models import Event
from events.utils import get_event

def event_list(request):
    events=Event.objects.all()
    context={'events': events}
    return render(request,'contribution/contribution.html',context)

def event_application(request, event_id):
    # TODO Once users are implemented, throw error when einreichung existiert
    if request.method == "POST":
        form = ContributionForm(event_id=event_id, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("base:index")
    else:
        form = ContributionForm(event_id=event_id)
    event = get_event(event_id)
    context = {'event': event, 'form': form}
    return render(request,'contribution/application.html',context)