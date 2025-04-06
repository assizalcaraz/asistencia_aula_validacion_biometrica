from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('historial/', views.historial, name='historial'),
    path('ver_qr/', views.mostrar_qr, name='mostrar_qr'),
    path('generar_qr/', views.generar_qr, name='generar_qr'),
    path('qr/', views.qr_acceso, name='qr_acceso'),
    path('asistencia/', views.registrar_asistencia, name='registrar_asistencia'),  # <- ESTA FALTA
]
