from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("base.urls")),
    path('events/', include('events.urls')),
    path('submission/',include('submission.urls')),
    path('authentication/',include('authentication.urls')),
]
