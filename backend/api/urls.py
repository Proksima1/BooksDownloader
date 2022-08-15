from django.urls import path
from . import views

urlpatterns = [
    path('getBook/<int:id>', views.getBook, name='api-getBook')
]
