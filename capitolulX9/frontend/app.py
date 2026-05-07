from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
import socket

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

API_URL = os.getenv("API_URL", "http://api-service:5001")
POD_NAME = os.getenv("HOSTNAME", socket.gethostname())
NODE_NAME = os.getenv("NODE_NAME", "Unknown")


@app.route('/')
def index():
    notes = []
    api_status = "ok"
    try:
        resp = requests.get(f"{API_URL}/notes", timeout=3)
        resp.raise_for_status()
        notes = resp.json()
    except requests.exceptions.ConnectionError:
        api_status = "unreachable"
        flash("API-ul nu este disponibil momentan.", "warning")
    except Exception as e:
        api_status = f"error: {e}"
        flash(f"Eroare la contactarea API-ului: {e}", "danger")

    return render_template(
        'index.html',
        notes=notes,
        pod_name=POD_NAME,
        node_name=NODE_NAME,
        api_url=API_URL,
        api_status=api_status,
        note_count=len(notes),
    )


@app.route('/notes', methods=['POST'])
def create_note():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    if not title:
        flash("Titlul notei este obligatoriu.", "warning")
        return redirect(url_for('index'))
    try:
        requests.post(
            f"{API_URL}/notes",
            json={"title": title, "content": content},
            timeout=3,
        )
        flash(f'Nota "{title}" a fost adăugată.', "success")
    except Exception as e:
        flash(f"Eroare la creare: {e}", "danger")
    return redirect(url_for('index'))


@app.route('/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    try:
        requests.delete(f"{API_URL}/notes/{note_id}", timeout=3)
        flash("Nota a fost ștearsă.", "success")
    except Exception as e:
        flash(f"Eroare la ștergere: {e}", "danger")
    return redirect(url_for('index'))


@app.route('/health/live')
def liveness():
    return {"status": "alive", "pod": POD_NAME}, 200


@app.route('/health/ready')
def readiness():
    try:
        requests.get(f"{API_URL}/health/live", timeout=2)
        return {"status": "ready"}, 200
    except Exception as e:
        return {"status": "not ready", "reason": str(e)}, 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
