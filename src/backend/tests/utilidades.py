"""Ayudantes compartidos por las pruebas del backend (inicio de sesión y pedidos de ejemplo)."""

from datetime import datetime, timedelta, timezone

PASSWORDS = {
    "admin@test.pe": "Admin2026!",
    "operador@test.pe": "Operador2026!",
    "bodega.a@test.pe": "BodegaA2026!",
    "bodega.b@test.pe": "BodegaB2026!",
}


async def _login(client, email):
    res = await client.post("/api/auth/login", json={"email": email, "password": PASSWORDS[email]})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _pedido(bodega_id, peso_kg):
    ahora = datetime.now(timezone.utc)
    return {
        "bodega_id": bodega_id, "direccion": "Jr. Los Pinos 123, El Agustino",
        "latitud": -12.04, "longitud": -77.00, "peso_kg": peso_kg,
        "ventana_inicio": ahora.isoformat(),
        "ventana_fin": (ahora + timedelta(hours=2)).isoformat(),
    }
