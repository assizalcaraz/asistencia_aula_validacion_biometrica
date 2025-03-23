from django.db import models

class Estudiante(models.Model):
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    encoding = models.BinaryField()
    salt = models.BinaryField()
    registrado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.dni


class Asistencia(models.Model):
    dni = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    foto = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.dni} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
