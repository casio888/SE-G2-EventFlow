from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("Veranstalter Registrierung/", views.organizer_registration_view, name = "OrganizerRegistration"),
    path("Einreicher Registrierung/", views.contributer_registration_view, name = "ContributerRegistration")
]