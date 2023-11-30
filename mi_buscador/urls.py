# buscador/urls.py
from django.urls import path
from .views import buscar

urlpatterns = [
    path('mi_buscador/', buscar, name='buscar'),
]
