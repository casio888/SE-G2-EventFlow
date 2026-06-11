from django.urls import path
from . import views

urlpatterns = [
    path("", views.veranstaltungen_liste, name="veranstaltungen_liste"),
    path("erstellen/", views.veranstaltung_erstellen, name="veranstaltung_erstellen"),
    path("<int:id>/", views.veranstaltung_detail, name="veranstaltung_detail"),
    path("<int:id>/bearbeiten/", views.veranstaltung_bearbeiten, name="veranstaltung_bearbeiten"),
]
