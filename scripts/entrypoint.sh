#!/bin/sh

echo "✅ Ejecutando entrypoint.sh de Django"

# Esperar a que la DB esté lista (opcional)
# echo "⏳ Esperando a la base de datos..."
# while ! nc -z db 5432; do sleep 1; done
# echo "✅ Base de datos disponible"

# Aplicar migraciones
echo "🔧 Aplicando migraciones..."
python manage.py makemigrations asistencia --noinput
python manage.py migrate --noinput

# Recolectar archivos estáticos (opcional si usás collectstatic)
# python manage.py collectstatic --noinput

# Iniciar servidor
echo "🚀 Iniciando servidor en 0.0.0.0:8000"
exec python manage.py runserver 0.0.0.0:8000
