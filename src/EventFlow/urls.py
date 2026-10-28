from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("base.urls")),
    path('veranstaltungen/', include('events.urls')),
    path('einreichung/',include('contribution.urls')),
    path('Authentifizierung/',include('authentication.urls')),
]
