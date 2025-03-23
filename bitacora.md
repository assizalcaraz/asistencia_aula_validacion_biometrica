## 📅 2025-03-23

### ✅ Avances

- Sistema de asistencia facial funcional en entorno local.
- Reconocimiento facial implementado con `face_recognition`.
- Cifrado de encodings faciales con clave secreta mediante `Fernet`.
- Registro y validación de estudiantes por DNI, clave y selfie.
- Captura de selfie directamente desde el navegador (JS + `<canvas>`).
- Implementación de escaneo por código QR para acceder al sistema.
- Generación dinámica del QR con IP local.
- Acceso confirmado desde dispositivos móviles en red local.
- Despliegue vía Docker + Docker Compose + Nginx con HTTPS local.
- Certificados autofirmados en entorno de desarrollo.
- Se resolvió problema de CSRF y trusted origins en HTTPS.

### 🛠️ Problemas abordados

- `localhost` no resolvía en iPhone: solucionado generando QR con IP real.
- La cámara no mostraba imagen en Safari (iOS): aún en análisis.
- El contenedor Nginx fallaba por error de montaje: corregido el path.
- CSRF Token fallaba por `Origin`: agregado dinámicamente `192.168.X.X` a `CSRF_TRUSTED_ORIGINS`.

### 🔜 Próximos pasos

- [ ] Mejorar compatibilidad con cámara en iOS Safari.
- [ ] Agregar vista para visualizar asistencia por fecha.
- [ ] Añadir almacenamiento opcional en Google Sheets.
- [ ] Empaquetado como instalador local para docentes.
