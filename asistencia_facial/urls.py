from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from asistencia import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('asistencia.urls')),
    path('qr/', views.qr_acceso, name='qr_acceso'),
]

# En producción con collectstatic, servir archivos desde STATIC_ROOT si DEBUG está activo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
