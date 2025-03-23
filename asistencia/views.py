import os
import base64
import socket
import qrcode
import face_recognition
import numpy as np
from io import BytesIO
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from .models import Asistencia, Estudiante
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import hashlib
import secrets
import base64
import netifaces 


def derive_key_from_secret(secret: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


def index(request):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        clave = request.POST.get('clave')
        selfie_data = request.POST.get('selfie')

        if not dni or not clave or not selfie_data:
            return HttpResponse("Datos incompletos", status=400)

        unknown_image = face_recognition.load_image_file(BytesIO(base64.b64decode(selfie_data.split(',')[1])))
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        if not unknown_encodings:
            return HttpResponse("No se detectó rostro en la imagen enviada", status=400)
        unknown_encoding = unknown_encodings[0]

        try:
            estudiante = Estudiante.objects.get(dni=dni)
            key = derive_key_from_secret(clave, estudiante.salt)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(estudiante.encoding)
            known_encoding = np.frombuffer(decrypted, dtype=np.float64)

            match = face_recognition.compare_faces([known_encoding], unknown_encoding)[0]
            if not match:
                return HttpResponse("El rostro no coincide con el registrado o la clave es incorrecta", status=403)
        except Estudiante.DoesNotExist:
            # Nuevo estudiante: generar salt y guardar encoding cifrado
            salt = secrets.token_bytes(16)
            key = derive_key_from_secret(clave, salt)
            fernet = Fernet(key)
            encoding_bytes = unknown_encoding.astype(np.float64).tobytes()
            encrypted = fernet.encrypt(encoding_bytes)
            Estudiante.objects.create(dni=dni, encoding=encrypted, salt=salt)
        except Exception as e:
            return HttpResponse(f"Error procesando los datos: {str(e)}", status=500)

        Asistencia.objects.create(dni=dni, foto="capturada_con_selfie")
        return HttpResponse(f"Asistencia registrada para DNI {dni}")

    return render(request, 'index.html')


def historial(request):
    registros = Asistencia.objects.order_by('-timestamp')
    return render(request, 'historial.html', {'registros': registros})


 # asegurate de tenerlo en requirements.txt

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No se necesita que esté activa la IP, solo se usa para obtener la IP local correcta
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def qr_acceso(request):
    try:
        ip = os.environ.get("DJANGO_HOST_IP", "localhost")
        url = f"https://{ip}/"

        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return render(request, 'qr_dashboard.html', {
            'url': url,
            'qr_data': qr_base64
        })
    except Exception as e:
        return HttpResponseServerError(f"Error generando el QR: {str(e)}")