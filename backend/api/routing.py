from django.urls import path
from .consumers import WSSearch

ws_urlpattern = [
    path('ws/search', WSSearch.as_asgi()),
]