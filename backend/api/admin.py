from django.contrib import admin
from .models import Log, BooksToSearch, FoundBook, SearchRequest

# Register your models here.

admin.site.register(Log)
admin.site.register(BooksToSearch)
admin.site.register(FoundBook)
admin.site.register(SearchRequest)
