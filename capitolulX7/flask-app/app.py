from flask import Flask
import os
import socket

app = Flask(__name__)

request_count = 0


@app.route('/')
def hello():
    global request_count
    request_count += 1
    pod_name = os.getenv("HOSTNAME", socket.gethostname())
    node_name = os.getenv("NODE_NAME", "Unknown Node")
    return f"""
    <html>
    <head><title>Flask pe Kubernetes</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 60px; background: #f0f4f8;">
        <h1 style="color: #326ce5;">&#9096; Hello from Kubernetes!</h1>
        <div style="background: white; border-radius: 8px; padding: 30px; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p><strong>Pod:</strong> <code style="background:#eef;padding:2px 6px;border-radius:4px;">{pod_name}</code></p>
            <p><strong>Node:</strong> <code style="background:#eef;padding:2px 6px;border-radius:4px;">{node_name}</code></p>
            <p><strong>Cereri servite de acest pod:</strong> <code style="background:#eef;padding:2px 6px;border-radius:4px;">{request_count}</code></p>
        </div>
        <p style="color: #666; margin-top: 20px;">Reîmprospătați pagina pentru a vedea echilibrarea traficului între pod-uri!</p>
    </body>
    </html>
    """


@app.route('/health')
def health():
    return {"status": "ok", "pod": os.getenv("HOSTNAME", socket.gethostname())}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
