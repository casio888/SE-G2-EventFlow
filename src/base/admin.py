from django.contrib import admin
from authentication.models import CustomUserContributer,CustomUserOrganizer,Adress

# Register your models here.

admin.site.register(CustomUserOrganizer)
admin.site.register(CustomUserContributer)
admin.site.register(Adress)