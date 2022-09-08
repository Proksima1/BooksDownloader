from datetime import datetime

from django.contrib import admin
from django.db import models


class Log(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    message = models.TextField()

    def __str__(self):
        return self.message


class Book(models.Model):
    class Meta:
        verbose_name_plural = 'Found books'

    bookName = models.TextField(null=False, unique=True)
    bookAuthor = models.TextField(null=False)
    bookCover = models.TextField(null=False)
    bookLink = models.TextField(null=False)
    bookSize = models.IntegerField(null=True)
    book = models.FileField(null=True)

    def __str__(self):
        return f"Book: {self.bookName}"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('bookName', 'bookAuthor')


class SearchRequest(models.Model):
    class Meta:
        verbose_name_plural = 'Search requests'
        ordering = ["-timestamp"]

    searchRequest = models.TextField(null=False, unique=True)
    timestamp = models.DateTimeField(default=datetime.now)
    books = models.ManyToManyField(Book)

    def __str__(self):
        return f"Search Request: {self.searchRequest}"


@admin.register(SearchRequest)
class SearchRequestAdmin(admin.ModelAdmin):
    list_display = ('searchRequest', 'timestamp')