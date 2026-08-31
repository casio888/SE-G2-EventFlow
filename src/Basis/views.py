from django.shortcuts import render,redirect
from Authentifizierung.models import User
from veranstaltungen.models import Veranstaltung


#def index(request):
#    return render(request, "index.html")


def login_view(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST.get("email")).first()
        if user and user.check_password(request.POST.get("password")):
            user.angemeldet = True
            user.save()

            #print("Login erfolgreich für:", user.email)

            return redirect("Basis:index")
        else:
            
            #print("Ungültige Anmeldedaten für E-Mail:", request.POST.get("email"))

            return render(request, "login.html", {"error": "E-Mail oder Passwort ungültig."})
    return render(request, "login.html")

def index(request):
    event_list=list(Veranstaltung.objects.all()[:6])

    empty_event = {
    'titel': 'Demo',
    'beschreibung': 'Es fehlen Events',
    'start_datum': None,
    'end_datum': None,
    'ort': 'Hinterkleinsiestdenicht',
    }

    while len(event_list)< 6:
            event_list.append(empty_event)

    print(f"DEBUG:event_list Länge={len(event_list)}")
    print(f"DEBUG:Erstes Event ={event_list[0]}")         

    return render(request, "index.html",{'event_list':event_list})
# Veranstaltungen aufbauen Variante in veranstaltungen nachschauen
# Wenn nicht alle 6 Elemente füllbar, was dann?