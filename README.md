# Asistencia en Aulas Validada por Reconocimiento Biométrico y Código QR

Este proyecto implementa un sistema completo de validación de asistencia universitaria mediante reconocimiento facial, geolocalización y autenticación segura, todo accesible desde el navegador sin necesidad de instalar apps. Es accesible vía túnel Cloudflare, lo que permite certificados HTTPS válidos desde una notebook local.

---

## 🎯 Objetivo del Proyecto

Desarrollar un sistema de asistencia robusto que funcione en red local o internet, minimizando el fraude por reenvío de QR, suplantación de identidad o validación remota.

---

## 🧩 Tecnologías utilizadas

- Django 5 (backend)
- Docker + Docker Compose
- face_recognition + dlib (biometría)
- Cryptography (Fernet + PBKDF2HMAC)
- Cloudflare Tunnel (exposición pública)
- geopy (validación geográfica)
- HTML5 + JavaScript (cámara y ubicación)

---

## 🛠️ Flujo de funcionamiento

### 1. Generación de QR
- `/ver_qr_auto/` genera un QR dinámico cada 40 segundos.
- El QR lleva al estudiante al endpoint `/asistencia/?token=...`.

### 2. Validación de asistencia
- El estudiante escanea el QR desde su celular.
- El navegador solicita cámara y ubicación.
- Se captura selfie, se ingresa la clave secreta y se envía junto con coordenadas y token único.

### 3. Verificación
- Se valida token, IP, zona geográfica.
- Se descifra embedding facial usando la clave secreta.
- Se compara con la selfie en tiempo real.
- Si coincide, se registra la asistencia en la base de datos.

---

## 📍 Seguridad y Antifraude

- QR rotativo cada 40 segundos
- Validación facial y por clave secreta
- Verificación de IP y zona (dentro de 100m de FADU Ciudad Universitaria)
- Uso único por día del mismo dispositivo/token

---

## 💾 Almacenamiento

- Se registra:
  - DNI
  - Email
  - Embedding facial cifrado
  - Salt individual
  - Timestamp
  - IP
- Las selfies no se almacenan (efímeras)

---

## 👩‍🏫 Panel Docente

- URL: `/docente/`
- Crear y eliminar estudiantes
- Ver ausentes y presentes
- Revisar historial completo de asistencias

---

## 📉 Problemas abordados

- ❌ Reenvío de QR → mitigado con tokens únicos + IP
- ❌ Suplantación → biometría + clave cifrada
- ❌ Validación remota → validación geográfica por GPS/IP
- ❌ Expiración del túnel → monitoreo de Cloudflare Tunnel activo
- ❌ Geolocalización en iOS → modal con botón para forzar permisos

---

## 🔮 Posibles mejoras

- Autenticación SSO institucional
- Exportación a Google Sheets
- Integración con aulas virtuales
- Reconocimiento de voz como 3er factor

---

## ✍️ Autor

**José Assiz Alcaraz Baxter**  
[LinkedIn](https://www.linkedin.com/in/assizalcaraz) | [GitHub](https://github.com/assizalcaraz)
