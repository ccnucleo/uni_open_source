from django.contrib import admin
from .models import Profile

# Registramos el modelo para que aparezca en el panel
admin.site.register(Profile)