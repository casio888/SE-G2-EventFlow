from django.urls import path
from . import views

app_name = "Authentifizierung"

urlpatterns = [
    path("Registrierung/", views.registrierung_view, name = "Registrierung"),
]