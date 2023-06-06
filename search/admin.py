from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Playlist)
admin.site.register(Movie)
admin.site.register(Series)
admin.site.register(Season)