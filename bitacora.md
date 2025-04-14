## 📅 2025-04-11

### ✅ Avances

- Añadida validación geográfica mediante coordenadas GPS del dispositivo.
- Se solicita ubicación al estudiante y se valida proximidad a FADU Ciudad Universitaria.
- Implementación de función `dentro_de_radio` usando `geopy` para chequear distancia (por defecto 100 m).
- Integración de geolocalización en flujo de asistencia: lat/lon enviados vía `POST` desde el navegador.
- Se impide registrar asistencia si la ubicación no está dentro del rango definido.
- Estudiantes no pueden registrar más de una asistencia por día desde la misma IP.
- Mejora visual del formulario: diseño con cámara en fondo y campos sobrepuestos.
- Se asegura uso de cámara frontal y resolución mínima en dispositivos móviles.
- Captura automática de selfie y validación desde el navegador.
- Solución híbrida para mostrar QR dinámico: nuevo token generado cada 40 segundos.
- URL del QR permanece estable para escaneo en masa.
- Tokens no expiran por uso múltiple pero se valida asistencia única por IP/DNI/día.
- Panel docente muestra historial completo de asistencias, incluyendo fecha, hora, DNI y dirección IP.
- Panel docente expandido para incluir lista cronológica de asistencias.
- Se prepara entorno para entrevista laboral usando el sistema como MVP funcional.

### 🛠️ Problemas abordados

- Error `500` por `InvalidToken` al desencriptar embeddings: corregido manejo de tipo `bytes`.
- Error de "Faltan datos requeridos: ubicación" en iPhone: se detectó que no se solicitaban permisos correctamente.
- Solucionado mediante retraso en la validación hasta confirmarse ubicación.
- Problemas de compatibilidad con Safari y ubicación no resueltos del todo, mitigados con debug en tiempo real (`console.log`, `debug.innerText`).
- Solicitud explícita de ubicación vinculada ahora al botón "Presente".

### 🔜 Próximos pasos

- [ ] Forzar consentimiento de ubicación mediante botón explícito si no se obtiene automáticamente.
- [ ] Verificar fingerprint del navegador como segundo factor para evitar duplicados desde WhatsApp Web.
- [ ] Persistencia de tokens válidos por franja horaria (no solo por uso único).
- [ ] Exportar historial a Google Sheets vía API.
- [ ] Generar instalador `.exe` para Windows que ejecute Docker + Cloudflared.
- [ ] Asegurar despliegue continuo y documentación para onboarding de docentes.


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

- [x] Mejorar compatibilidad con cámara en iOS Safari.
- [x] Agregar vista para visualizar asistencia por fecha.
- [ ] Añadir almacenamiento opcional en Google Sheets.
- [ ] Empaquetado como instalador local para docentes.
