"""
API minimal pentru laboratorul de Load Balancers.
Returnează identitatea pod-ului (hostname, IP în cluster) pentru a observa distribuția traficului.
"""

import logging
import os
import socket

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="Laborator LB API", version="1.0.0")


def _pod_hostname() -> str:
    """În Kubernetes, HOSTNAME este de obicei numele pod-ului."""
    return os.getenv("HOSTNAME") or socket.gethostname()


@app.get("/")
def hello():
    """
    Endpoint principal: vizibil în bucle de curl către echilibratorul de sarcină.
    """
    hostname = _pod_hostname()
    pod_ip = os.getenv("POD_IP", "")
    message = (
        "Salut de la API-ul de laborator (load balancing). "
        "Fiecare replică răspunde cu hostname-ul său unic."
    )
    return {
        "message": message,
        "hostname": hostname,
        "pod_ip": pod_ip,
        "kubernetes": bool(os.getenv("KUBERNETES_SERVICE_HOST")),
    }


@app.get("/health")
def health():
    """Pentru liveness/readiness probes."""
    return {"status": "ok", "pod": _pod_hostname()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
