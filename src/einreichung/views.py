from django.shortcuts import render
from .models import Event

def event_list(request):
    events=Event.object.all()
    context={'events': events}
    return render(request,'einreichung/einreichung.html',context)
# Create your views here.
