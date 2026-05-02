import os
import httpx
from dotenv import load_dotenv

load_dotenv()

NOTIFICATIONS_SERVICE_URL = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://localhost:8003")


def publicar_notificacion(folio: str, cliente_id: int, total: float, url_descarga: str):
    payload = {
        "folio": folio,
        "cliente_id": cliente_id,
        "total": total,
        "url_descarga": url_descarga,
    }
    try:
        response = httpx.post(f"{NOTIFICATIONS_SERVICE_URL}/notificaciones/", json=payload)
        response.raise_for_status()
    except httpx.RequestError:
        raise Exception("Notifications service no disponible")
    except httpx.HTTPStatusError as e:
        raise Exception(f"Error en notifications service: {e.response.text}")
