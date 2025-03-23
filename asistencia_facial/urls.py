from django.contrib import admin
from django.urls import path, include
from asistencia import views  # necesario para el QR

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('asistencia.urls')),          # index y historial
    path('qr/', views.qr_acceso, name='qr_acceso') # vista para mostrar el QR
]
