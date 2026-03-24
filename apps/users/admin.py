from django.contrib import admin
from .models import User, SearchPreference

admin.site.register(User)
admin.site.register(SearchPreference)