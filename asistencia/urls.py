from django.urls import path
from . import views

urlpatterns = [

    path("ver_qr_auto/", views.mostrar_qr_auto, name="mostrar_qr_auto"),  #VISUALIZAR QR AUTOMATICO 
    path('docente/', views.docente, name='docente'), #PANEL DEL DOCENTE 
    







    path('', views.index, name='index'),
    path('historial/', views.historial, name='historial'),
    path('ver_qr/', views.mostrar_qr, name='mostrar_qr'),
    path('generar_qr/', views.generar_qr, name='generar_qr'),
    path('qr/', views.qr_acceso, name='qr_acceso'),
    path('registro/', views.registro, name='registro'),  # <- CORREGIDO
    path('asistencia/', views.registrar_asistencia, name='asistencia'),

    
    path("obtener_qr_dinamico/", views.obtener_qr_dinamico, name="obtener_qr_dinamico"),



    path('logout/', views.logout, name='logout'),

]
