from flask import Flask, jsonify
import redis
import os
import socket

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
APP_TITLE = os.getenv("APP_TITLE", "Contor de vizite")

# Conexiunea la Redis este stabilita o singura data la pornirea aplicatiei
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.route('/')
def index():
    pod_name = os.getenv("HOSTNAME", socket.gethostname())
    node_name = os.getenv("NODE_NAME", "Unknown Node")
    try:
        count = r.incr("hits")
        redis_status = "OK"
    except redis.exceptions.RedisError as e:
        count = "N/A"
        redis_status = f"EROARE: {e}"

    return f"""
    <html>
    <head><title>{APP_TITLE}</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 60px; background: #f0f4f8;">
        <h1 style="color: #326ce5;">&#128202; {APP_TITLE}</h1>
        <div style="background: white; border-radius: 8px; padding: 30px; display: inline-block;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 400px;">
            <h2 style="font-size: 3em; color: #e44d26; margin: 10px 0;">{count}</h2>
            <p style="color: #666;">cereri totale (numărate în Redis)</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p><strong>Pod:</strong> <code style="background:#eef;padding:2px 8px;border-radius:4px;">{pod_name}</code></p>
            <p><strong>Node:</strong> <code style="background:#eef;padding:2px 8px;border-radius:4px;">{node_name}</code></p>
            <p><strong>Redis ({REDIS_HOST}:{REDIS_PORT}):</strong>
               <code style="background:#eef;padding:2px 8px;border-radius:4px;">{redis_status}</code></p>
        </div>
        <p style="color: #888; margin-top: 20px; font-size: 0.9em;">
            Reîmprospătați pagina — pod-ul se schimbă, contorul crește continuu!
        </p>
    </body>
    </html>
    """


@app.route('/reset')
def reset():
    """Resetează contorul de vizite la zero."""
    r.set("hits", 0)
    return jsonify({"status": "reset", "hits": 0}), 200


@app.route('/health/live')
def liveness():
    """Liveness probe: verifică dacă procesul Flask rulează."""
    return jsonify({"status": "alive", "pod": os.getenv("HOSTNAME")}), 200


@app.route('/health/ready')
def readiness():
    """
    Readiness probe: verifică dacă aplicatia POATE servi cereri.
    Un pod nu va primi trafic cata vreme Redis nu este disponibil.
    """
    try:
        r.ping()
        return jsonify({"status": "ready", "redis": "ok"}), 200
    except redis.exceptions.RedisError as e:
        return jsonify({"status": "not ready", "redis": str(e)}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
