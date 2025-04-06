from flask import Flask, jsonify
import subprocess
import threading
import re

app = Flask(__name__)
tunnel_url = {"url": None}

def run_cloudflared():
    global tunnel_url
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://web:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    for line in process.stdout:
        print(line.strip())
        match = re.search(r"(https://[a-zA-Z0-9\-]+\.trycloudflare\.com)", line)
        if match:
            tunnel_url["url"] = match.group(1)

# Lanza cloudflared en segundo plano
threading.Thread(target=run_cloudflared, daemon=True).start()

@app.route("/tunnel_url.json")
def get_tunnel_url():
    if tunnel_url["url"]:
        return jsonify({"url": tunnel_url["url"]})
    return jsonify({"error": "No se pudo obtener la URL del túnel."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
