#!/bin/sh

echo "✅ Ejecutando cloudflared-entry.sh"
echo "🌐 Iniciando túnel Cloudflare..."

# Limpiar el archivo de destino
echo "" > /tunnel_data/tunnel_url.txt

# Ejecutar cloudflared y capturar salida
cloudflared tunnel --url http://web:8000 --no-autoupdate 2>&1 | tee /tunnel_data/tunnel_url.log | \
while read line; do
    echo "$line"
    echo "$line" | grep -o 'https://.*trycloudflare.com' >> /tunnel_data/tunnel_url.txt
done
