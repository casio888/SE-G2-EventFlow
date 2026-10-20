from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path("erstellen/", views.event_create, name="event_create"),
    path("<int:id>/", views.event_detail, name="event_detail"),
    path("deine-events/", views.events_your_events, name="events_your_events"), 
    path("<int:id>/bearbeiten/", views.event_edit, name="event_edit"),
]
