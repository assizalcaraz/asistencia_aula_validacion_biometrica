from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),                # formulario de asistencia
    path('historial/', views.historial, name='historial')  # vista de historial
]
