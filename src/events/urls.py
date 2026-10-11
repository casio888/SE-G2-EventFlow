from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path("create/", views.veranstaltung_create, name="veranstaltung_create"),
    path("<int:id>/", views.veranstaltung_detail, name="veranstaltung_detail"),
    path("your-events/", views.events_your_events, name="events_your_events"), 
    path("<int:id>/edit/", views.veranstaltung_edit, name="veranstaltung_edit"),
]
