from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("Basis.urls")),
    path('veranstaltungen/', include('veranstaltungen.urls')),
    path('einreichung/',include('einreichung.urls')),
]
