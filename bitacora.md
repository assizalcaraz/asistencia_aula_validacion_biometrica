## 📅 2025-04-06

### ✅ Avances

- Sistema de asistencia biométrica funcional en entorno local.
- Reconocimiento facial usando `face_recognition` con `dlib`.
- Encodings cifrados con clave derivada del DNI + clave secreta (`PBKDF2` + `Fernet`).
- Registro de estudiantes con captura de selfie desde el navegador.
- Validación de asistencia mediante comparación facial en tiempo real.
- Redirección automática a `/registro/` si el DNI no está registrado.
- Registro automático de asistencia al finalizar el alta del estudiante.
- Panel `/docente/` con CRUD básico de estudiantes.
- Listado de estudiantes sin asistencia (faltantes) con contador.
- Migraciones automatizadas desde `entrypoint.sh`.
- Validación de tokens únicos de un solo uso (proximidad aula).
- Diseño responsive compatible con dispositivos móviles.

### 🛠️ Problemas abordados

- Importaciones circulares al organizar `models.py` y `views.py`.
- Error `models not defined` en vista `docente`: resuelto.
- Token no se enviaba correctamente al formulario: corregido.
- Error `csrf_exempt` no definido: solucionado importando desde `django.views.decorators.csrf`.

### 🔜 Próximos pasos

- [ ] Bloquear múltiples DNIs registrados con una misma cara.
- [ ] Bloquear múltiples caras para un mismo DNI.
- [ ] Mostrar historial detallado por fecha.
- [ ] Exportar asistencias a Google Sheets.
- [ ] Empaquetar como solución lista para docentes no técnicos.


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
