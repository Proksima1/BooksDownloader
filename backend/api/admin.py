from django.contrib import admin
from .models import Log, LogAdmin
# Register your models here.


admin.site.register(Log, LogAdmin)