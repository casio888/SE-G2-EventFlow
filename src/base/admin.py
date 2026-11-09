from django.contrib import admin
from authentication.models import CustomUserContributer,CustomUserOrganizer,Address

# Register your models here.

admin.site.register(CustomUserOrganizer)
admin.site.register(CustomUserContributer)
admin.site.register(Address)