from datetime import datetime

from django.contrib import admin
from django.db import models


class Log(models.Model):
    levels = [(0, "DEBUG"),
              (1, "INFO"),
              (2, 'WARNING'),
              (3, "ERROR")]
    timestamp = models.DateTimeField(default=datetime.now)
    message = models.TextField()
    level = models.IntegerField(default=1, choices=levels)
    """Level: 0 - DEBUG
              1 - INFO
              2 - WARNING
              3 - ERROR"""

    def format_timestamp(self):
        return self.timestamp.strftime("%d/%m/%Y %H:%M:%S")

    def view_level(self):
        return self.levels[self.level]

    def __str__(self):
        return self.message


class LogAdmin(admin.ModelAdmin):
    list_display = ('format_timestamp', 'message', 'level',)


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

    searchRequest = models.TextField(unique=True)
    timestamp = models.DateTimeField(default=datetime.now)
    books = models.ManyToManyField(Book)

    def __str__(self):
        return f"Search Request: {self.searchRequest}"


@admin.register(SearchRequest)
class SearchRequestAdmin(admin.ModelAdmin):
    list_display = ('searchRequest', 'timestamp')
