from django.urls import path
from . import views

app_name = 'veranstaltungen'

urlpatterns = [
    path("", views.veranstaltungen_liste, name="veranstaltungen_liste"),
    path("erstellen/", views.veranstaltung_erstellen, name="veranstaltung_erstellen"),
    path("<int:id>/", views.veranstaltung_detail, name="veranstaltung_detail"),
    path("deine-events/", views.veranstaltungen_your_events, name="veranstaltungen_your_events"),
]   
