from django.shortcuts import render,redirect
from Authentifizierung.models import User

def index(request):
    return render(request, "index.html")


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
