from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres-service"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "notesdb"),
    "user": os.getenv("DB_USER", "notes_user"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db(retries: int = 15, delay: int = 3):
    """Create schema on startup, with retries for slow DB starts."""
    for attempt in range(1, retries + 1):
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id         SERIAL PRIMARY KEY,
                        title      VARCHAR(255) NOT NULL,
                        content    TEXT         DEFAULT '',
                        created_at TIMESTAMPTZ  DEFAULT NOW()
                    )
                """)
            conn.commit()
            conn.close()
            log.info("Schema initialized successfully.")
            return
        except psycopg2.OperationalError as e:
            log.warning("DB not ready (attempt %d/%d): %s", attempt, retries, e)
            time.sleep(delay)
    raise RuntimeError("Could not connect to PostgreSQL after %d attempts." % retries)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/notes', methods=['GET'])
def list_notes():
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC")
        notes = cur.fetchall()
    conn.close()
    return jsonify([dict(n) for n in notes])


@app.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json(force=True)
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING id, created_at",
            (title, content),
        )
        row = cur.fetchone()
    conn.commit()
    conn.close()
    log.info("Created note id=%d title=%r", row[0], title)
    return jsonify({"id": row[0], "title": title, "content": content, "created_at": str(row[1])}), 201


@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, title, content, created_at FROM notes WHERE id = %s", (note_id,))
        note = cur.fetchone()
    conn.close()
    if note is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(note))


@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        deleted = cur.rowcount
    conn.commit()
    conn.close()
    if deleted == 0:
        return jsonify({"error": "not found"}), 404
    log.info("Deleted note id=%d", note_id)
    return '', 204


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------

@app.route('/health/live')
def liveness():
    return jsonify({"status": "alive", "pod": os.getenv("HOSTNAME")}), 200


@app.route('/health/ready')
def readiness():
    try:
        conn = get_conn()
        conn.close()
        return jsonify({"status": "ready", "db": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "not ready", "db": str(e)}), 503


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=False)
