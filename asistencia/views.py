# Librerías estándar
import os
import socket
import base64
import secrets
from io import BytesIO
import traceback
from datetime import datetime

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
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.db import models

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
from geopy.distance import geodesic

# Modelos locales
from .models import Asistencia, Estudiante, TokenAcceso


# Coordenadas de FADU
FADU_COORDS = (-34.54212801201143, -58.444688376739656)
RADIO_METROS = 100  # configurable



def dentro_de_radio(lat, lon, centro=FADU_COORDS, radio=RADIO_METROS):
    try:
        ubicacion_usuario = (float(lat), float(lon))
        distancia = geodesic(centro, ubicacion_usuario).meters
        return distancia <= radio
    except Exception as e:
        print(f"[ERROR] Validando geolocalización: {e}")
        return False


def index(request):
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Token no proporcionado", status=400)

    if request.method == "GET":
        return render(request, "index.html", {"token": token})

def generar_clave(clave_usuario):
    from hashlib import sha256
    hash = sha256(clave_usuario.encode()).digest()
    return base64.urlsafe_b64encode(hash)

def derive_key_from_secret(secret, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))

def derive_system_key():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'static_salt_123',
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))


def registro(request):
    if request.method == "GET":
        dni = request.session.get('registro_dni', '')
        clave = request.session.get('registro_clave', '')
        selfie = request.session.get('registro_selfie', '')
        token = request.session.get('registro_token', '')
        return render(request, 'registro.html', {
            "dni": dni,
            "clave": clave,
            "selfie": selfie,
            "token": token
        })

    elif request.method == "POST":
        dni = request.POST.get("dni")
        clave = request.POST.get("clave")
        email = request.POST.get("email")
        selfie_data = request.POST.get("selfie")
        token = request.POST.get("token")

        try:
            header, encoded = selfie_data.split(',', 1)
            image_data = base64.b64decode(encoded)
            image_array = np.array(face_recognition.load_image_file(BytesIO(image_data)))
            encoding = face_recognition.face_encodings(image_array)[0]
        except Exception as e:
            return HttpResponse(f"Error al procesar la selfie: {str(e)}", status=400)

        # Rechazar si el rostro ya está registrado con otro DNI
        system_key = derive_system_key()
        fernet_sys = Fernet(system_key)

        for est in Estudiante.objects.all():
            try:
                decrypted = fernet_sys.decrypt(est.encoding)
                existing_encoding = np.frombuffer(decrypted, dtype=np.float64)
                if face_recognition.compare_faces([existing_encoding], encoding)[0]:
                    return HttpResponse("Este rostro ya está registrado con otro DNI.", status=409)
            except Exception:
                continue

        # Encriptar el encoding con la clave del sistema para poder hacer comparación futura
        encrypted_encoding = fernet_sys.encrypt(encoding.tobytes())
        salt = b'static_salt_123'  # puede hacerse dinámico si se desea reforzar, pero ya tenemos clave única

        Estudiante.objects.create(
            dni=dni,
            email=email,
            encoding=encrypted_encoding,
            salt=salt
        )

        Asistencia.objects.create(dni=dni, foto="capturada_por_selfie")

        try:
            acceso = TokenAcceso.objects.get(token=token)
            acceso.usado = True
            acceso.save()
        except TokenAcceso.DoesNotExist:
            pass

        request.session["dni"] = dni
        messages.success(request, "Estudiante registrado y asistencia marcada correctamente.")
        return redirect("historial")

    return HttpResponse("Método no permitido", status=405)


def historial(request):
    dni = request.session.get("dni")
    if not dni:
        return redirect("index")

    asistencias = Asistencia.objects.filter(dni=dni).order_by("-timestamp")
    return render(request, "historial.html", {"asistencias": asistencias, "dni": dni})




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

    # Agrega el token si no existe
    if not TokenAcceso.objects.filter(token=token).exists():
        TokenAcceso.objects.create(
            token=token,
            vencimiento=300,
            creado=timezone.now(),
            usado=False
        )

    url_completa = f"{url_base}/asistencia/?token={token}"

    qr = qrcode.make(url_completa)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "mostrar_qr.html", {
        "qr_base64": img_str,
        "url_completa": url_completa
    })

...

@csrf_exempt
def docente(request):
    if request.method == "POST":
        accion = request.POST.get("accion")
        dni = request.POST.get("dni")
        email = request.POST.get("email", "")

        if accion == "crear" and dni:
            if not Estudiante.objects.filter(dni=dni).exists():
                fake_key = Fernet.generate_key()
                fake_encoding = Fernet(fake_key).encrypt(b"placeholder_encoding")
                Estudiante.objects.create(dni=dni, email=email, encoding=fake_encoding, salt=os.urandom(16))
        elif accion == "eliminar" and dni:
            Estudiante.objects.filter(dni=dni).delete()

    estudiantes = Estudiante.objects.all().order_by("dni")

    asistencias = Asistencia.objects.values("dni").annotate(
        total=models.Count("id")
    )
    asistencias_dict = {a["dni"]: a["total"] for a in asistencias}

    estudiantes_faltas = []
    for estudiante in estudiantes:
        dni = estudiante.dni
        total_asistencias = asistencias_dict.get(dni, 0)
        if total_asistencias == 0:
            estudiantes_faltas.append({
                "dni": dni,
                "email": estudiante.email,
                "faltas": "Ninguna asistencia"
            })

    # Nueva sección: obtener todas las asistencias ordenadas cronológicamente
    asistencias_cronologicas = Asistencia.objects.all().order_by("-timestamp")

    return render(request, "docente.html", {
        "estudiantes": estudiantes,
        "faltantes": estudiantes_faltas,
        "asistencias_cronologicas": asistencias_cronologicas,
    })

    
def logout(request):
    request.session.flush()
    return redirect("index")

# Variables de control
HORARIO_HABILITADO = os.environ.get("HORARIO_HABILITADO", "00:20-23:00")
DIA_HABILITADO = os.environ.get("DIA_HABILITADO", "4")  #0 = Lunes



def asistencia_habilitada():
    ahora = datetime.now()
    dia_actual = str(ahora.weekday())
    hora_actual = ahora.time()
    desde_str, hasta_str = HORARIO_HABILITADO.split("-")
    desde = datetime.strptime(desde_str, "%H:%M").time()
    hasta = datetime.strptime(hasta_str, "%H:%M").time()
    print ("la hora es", ahora)
    return dia_actual == DIA_HABILITADO and desde <= hora_actual <= hasta

def mostrar_qr_auto(request):
    return render(request, "mostrar_qr_auto.html")

def obtener_qr_dinamico(request):
    if not asistencia_habilitada():
        return JsonResponse({"error": "Fuera de horario permitido"}, status=403)
        
        
        

    url_base = obtener_url_cloudflare()
    nuevo_token = secrets.token_urlsafe(16)

    TokenAcceso.objects.create(
        token=nuevo_token,
        vencimiento=300,
        creado=timezone.now(),
        usado=False
    )
    url_completa = f"{url_base}/asistencia/?token={nuevo_token}"

    qr = qrcode.make(url_completa)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return JsonResponse({
        "qr_base64": img_str,
        "url_completa": url_completa
    })



def registrar_asistencia(request):
    if request.method == "POST":
        dni = request.POST.get("dni")
        clave = request.POST.get("clave")
        selfie_data = request.POST.get("selfie")
        token = request.GET.get("token") or request.POST.get("token")
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")

        faltantes = []
        if not dni: faltantes.append("dni")
        if not clave: faltantes.append("clave")
        if not selfie_data: faltantes.append("selfie")
        if not token: faltantes.append("token")
        if not lat or not lon: faltantes.append("ubicación")

        if faltantes:
            return HttpResponse(f"Faltan datos requeridos: {', '.join(faltantes)}", status=400)

        # ✅ Validar cercanía física al aula (FADU)
        if not dentro_de_radio(lat, lon):
            return HttpResponse("Debés estar físicamente presente en la zona habilitada (FADU)", status=403)

        try:
            acceso = TokenAcceso.objects.get(token=token)
        except TokenAcceso.DoesNotExist:
            return HttpResponse("Token inválido", status=403)

        ahora = timezone.now()
        if (ahora - acceso.creado).total_seconds() > acceso.vencimiento:
            return HttpResponse("Token expirado", status=403)

        try:
            selfie_bytes = base64.b64decode(selfie_data.split(",")[1])
            img = face_recognition.load_image_file(BytesIO(selfie_bytes))
            if img.shape[0] < 240 or img.shape[1] < 240:
                return HttpResponse("La imagen es demasiado pequeña. Usa la cámara frontal con buena luz.", status=400)

            encodings = face_recognition.face_encodings(img)
            if not encodings:
                return HttpResponse("No se detectó un rostro válido", status=400)
            unknown_encoding = encodings[0]
        except Exception as e:
            print(f"[ERROR] Procesando selfie: {e}")
            return HttpResponse("Error al procesar la imagen", status=400)

        try:
            estudiante = Estudiante.objects.get(dni=dni)
            print(f"[DEBUG] Estudiante encontrado: {estudiante.dni}")

            if isinstance(estudiante.salt, str):
                estudiante_salt = estudiante.salt.encode()
            else:
                estudiante_salt = estudiante.salt

            print(f"[DEBUG] Salt (type={type(estudiante_salt)}): {estudiante_salt}")

            key = derive_key_from_secret(clave, estudiante_salt)
            f = Fernet(key)

            print("[DEBUG] Intentando descifrar encoding...")
            encoding_bytes = estudiante.encoding
            if isinstance(encoding_bytes, memoryview):
                encoding_bytes = encoding_bytes.tobytes()
            elif isinstance(encoding_bytes, str):
                encoding_bytes = encoding_bytes.encode()

            decrypted = f.decrypt(encoding_bytes)
            print("[DEBUG] Encoding descifrado correctamente.")

            known_encoding = np.frombuffer(decrypted, dtype=np.float64)
            print(f"[DEBUG] known_encoding: {known_encoding[:5]}...")

            match = face_recognition.compare_faces([known_encoding], unknown_encoding)[0]
            print(f"[DEBUG] Resultado de comparación facial: {match}")

            if not match:
                return HttpResponse("El rostro no coincide o la clave es incorrecta", status=403)

            ip = request.META.get("REMOTE_ADDR")
            hoy = timezone.now().date()
            if Asistencia.objects.filter(dni=dni, ip=ip, timestamp__date=hoy).exists():
                return HttpResponse("Ya registraste asistencia hoy desde este dispositivo", status=403)

            Asistencia.objects.create(dni=dni, foto="capturada_por_selfie", ip=ip)
            request.session["dni"] = dni
            return redirect("historial")

        except Estudiante.DoesNotExist:
            print("[DEBUG] Estudiante no registrado. Redirigiendo a registro.")
            request.session['registro_dni'] = dni
            request.session['registro_clave'] = clave
            request.session['registro_selfie'] = selfie_data
            request.session['registro_token'] = token
            return redirect('registro')

        except Exception as e:
            print(f"[ERROR] Validando asistencia: {e}")
            traceback.print_exc()
            return HttpResponse(f"Error interno: {str(e)}", status=500)

    token = request.GET.get("token", "")
    return render(request, "index.html", {"token": token})
