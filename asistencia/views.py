# Librerías estándar
import os
import socket
import base64
import secrets
from io import BytesIO

# Librerías de terceros
import qrcode
import numpy as np
import netifaces
import face_recognition
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Django
from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages



# Modelos locales
from .models import Asistencia, Estudiante

def generar_clave(clave_usuario):
    from hashlib import sha256
    hash = sha256(clave_usuario.encode()).digest()
    return base64.urlsafe_b64encode(hash)

@csrf_exempt  # Si estás en desarrollo y necesitás testear sin CSRF
def registrar_estudiante(request):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        clave = request.POST.get('clave')
        selfie_base64 = request.POST.get('selfie')

        if not selfie_base64 or not dni or not clave:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'registro.html')

        if Estudiante.objects.filter(dni=dni).exists():
            messages.error(request, "Ese DNI ya está registrado.")
            return render(request, 'registro.html')

        # Convertir imagen a array numpy
        try:
            formato, datos = selfie_base64.split(';base64,')
            imagen_bytes = base64.b64decode(datos)
            np_arr = np.frombuffer(imagen_bytes, np.uint8)
            import cv2
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception:
            messages.error(request, "Error al procesar la imagen.")
            return render(request, 'registro.html')

        # Extraer encoding facial
        try:
            encoding = face_recognition.face_encodings(rgb_img)[0]
        except IndexError:
            messages.error(request, "No se detectó un rostro válido.")
            return render(request, 'registro.html')

        # Cifrar el encoding con clave
        clave_cifrado = generar_clave(clave)
        f = Fernet(clave_cifrado)
        encoding_bytes = encoding.tobytes()
        encoding_cifrado = f.encrypt(encoding_bytes)

        # Verificar si ya hay un encoding igual
        estudiantes = Estudiante.objects.all()
        for est in estudiantes:
            try:
                f_test = Fernet(clave_cifrado)
                encoding_descifrado = f_test.decrypt(est.encoding)
                e2 = np.frombuffer(encoding_descifrado, dtype=np.float64)
                distancia = np.linalg.norm(encoding - e2)
                if distancia < 0.5:
                    messages.error(request, "Esa cara ya está registrada con otro DNI.")
                    return render(request, 'registro.html')
            except Exception:
                continue  # No se puede descifrar => no es la misma clave => se ignora

        # Guardar en DB
        Estudiante.objects.create(
            dni=dni,
            encoding=encoding_cifrado,
            salt=b'',  # Placeholder si luego implementás salting manual
        )
        messages.success(request, "✅ Registro exitoso.")
        return redirect('asistencia')

    return render(request, 'registro.html')



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

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip



@csrf_exempt
def registrar_asistencia(request):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        clave = request.POST.get('clave')
        selfie_data = request.POST.get('selfie')
        token = request.GET.get("token", "no-token")

        if not dni or not clave or not selfie_data:
            return HttpResponse("Faltan datos requeridos", status=400)

        # Procesar la selfie recibida
        try:
            selfie_bytes = base64.b64decode(selfie_data.split(",")[1])
            img = face_recognition.load_image_file(BytesIO(selfie_bytes))
            unknown_encoding = face_recognition.face_encodings(img)[0]
        except Exception:
            return HttpResponse("No se detectó un rostro válido", status=400)

        # Buscar estudiante y validar rostro
        try:
            estudiante = Estudiante.objects.get(dni=dni)
            key = derive_key_from_secret(clave, estudiante.salt)
            f = Fernet(key)
            decrypted = f.decrypt(estudiante.encoding)
            known_encoding = np.frombuffer(decrypted, dtype=np.float64)

            match = face_recognition.compare_faces([known_encoding], unknown_encoding)[0]
            if not match:
                return HttpResponse("El rostro no coincide o la clave es incorrecta", status=403)

            # Si todo está bien, registrar asistencia
            Asistencia.objects.create(dni=dni, foto="capturada_por_selfie")
            return HttpResponse(f"✅ Asistencia registrada correctamente para {dni} con token {token}")

        except Estudiante.DoesNotExist:
            return HttpResponse("DNI no registrado", status=404)
        except Exception as e:
            return HttpResponse(f"Error interno: {str(e)}", status=500)

    return render(request, "asistencia.html")  # Formulario HTML que pide DNI, clave y selfie


def qr_acceso(request):
    try:
        tunnel_file = "/app/tmp/tunnel_url.txt"
        if not os.path.exists(tunnel_file):
            return HttpResponseServerError("No se encontró el túnel activo.")

        tunnel_url = None
        with open(tunnel_file, "r") as f:
            for line in f:
                if "trycloudflare.com" in line:
                    tunnel_url = line.strip()
                    break

        if not tunnel_url:
            return HttpResponseServerError("No se pudo obtener la URL del túnel.")

        url_final = f"{tunnel_url}/verificacion"

        qr = qrcode.make(url_final)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        return render(request, "qr_dashboard.html", {
            "qr_img": img_base64,
            "url": url_final,
        })

    except Exception as e:
        return HttpResponseServerError(f"Error generando QR: {str(e)}")



def obtener_url_cloudflare():
    try:
        with open("/tunnel_data/tunnel_url.txt", "r") as f:
            contenido = f.read().strip()
            print(f"📦 Leído desde archivo: {contenido}")
            return contenido
    except FileNotFoundError:
        print("🚫 Archivo no encontrado")
        return "URL no disponible"




def generar_qr(request):
    try:
        ruta_log = "/app/tmp/tunnel_url.txt"

        if not os.path.exists(ruta_log):
            print("❌ El archivo tunnel_url.txt no existe")
            return HttpResponse("Archivo no encontrado", status=500)

        with open(ruta_log, "r") as f:
            url = f.read().strip()

        print(f"✅ URL obtenida desde el archivo: {url}")

        if not url.startswith("http"):
            print("❌ La URL no parece válida")
            return HttpResponse("URL inválida", status=500)

        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        buffer.seek(0)
        print("✅ QR generado correctamente")
        return HttpResponse(buffer.getvalue(), content_type="image/png")

    except Exception as e:
        print(f"🔥 Error en generar_qr: {e}")
        return HttpResponse("Error interno del servidor", status=500)

def mostrar_qr(request):
    url_base = obtener_url_cloudflare()
    token = "token-de-ejemplo"
    url_completa = f"{url_base}/asistencia/?token={token}"

    # Generar QR en memoria
    qr = qrcode.make(url_completa)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "mostrar_qr.html", {
        "qr_base64": img_str,
        "url_completa": url_completa
    })