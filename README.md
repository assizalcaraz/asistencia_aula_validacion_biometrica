```markdown
# Asistencia Facial con Reconocimiento Biométrico y Código QR

Este proyecto permite registrar asistencia en el aula escaneando un código QR, accediendo a una interfaz web local que utiliza reconocimiento facial y validación mediante clave secreta.

## Funcionalidades principales

- ✅ Registro de estudiantes con imagen facial y clave cifrada.
- ✅ Validación de asistencia mediante selfie y clave.
- ✅ Generación dinámica de código QR con la IP local del servidor.
- ✅ Interfaz accesible desde celulares (funciona en red local o hotspot).
- ✅ Captura de cámara directamente en el navegador (sin app instalada).
- ✅ Docker + Nginx + Django para despliegue local con HTTPS.

## Tecnologías utilizadas

- Django
- OpenCV + face_recognition
- Docker & Docker Compose
- Nginx (reverse proxy con certificados autofirmados)
- SQLite (para desarrollo)
- HTML5 + JS (captura de cámara en navegador)

## Cómo ejecutar

```bash
docker compose down
docker compose build
docker compose up -d
```

Asegurate de acceder desde un dispositivo conectado a la misma red local.

## Recomendaciones de seguridad

- Validar configuración del firewall si se usa en red compartida.
- Verificar certificados HTTPS si se accede desde dispositivos Apple.
- Se recomienda mover a producción con certificados reales (Let’s Encrypt).
```

