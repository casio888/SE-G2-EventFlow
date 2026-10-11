from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("registration/", views.registration_view, name = "registration"),
]