import os
from pathlib import Path

# Cargar Backend/.env con override antes que core/email u otros (evita MERCADOPAGO_* heredados del sistema).
import database  # noqa: F401

from fastapi import FastAPI

# Path base del backend (donde está main.py)
BASE_DIR = Path(__file__).resolve().parent
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.email import enviar_email_confirmacion

from routers import (
    clientes,
    barberos,
    visitas,
    horarios,
    servicios,
    auth,
    admin,
    perfil,
    estadisticas,
    carousel,
    tv,
)

app = FastAPI(
    title="API Barbería",
    version="1.0.0",
)

# =======================
# TEST EMAIL (solo si ENABLE_TEST_EMAIL=true en .env)
# =======================
if os.getenv("ENABLE_TEST_EMAIL", "").lower() in ("true", "1", "yes"):
    @app.get("/test-email")
    async def test_email():
        await enviar_email_confirmacion(
            destinatario="tuemail@gmail.com",
            asunto="Test Barbería",
            cuerpo="Este es un email de prueba desde FastAPI.",
        )
        return {"status": "email enviado"}


# =======================
# STATIC FILES (MEDIA)
# =======================
# 👉 URLs públicas: /media/...
# 👉 Disco real: static/...

# Rutas absolutas para que funcione desde cualquier CWD (producción)
STATIC_DIR = BASE_DIR / "static"
(STATIC_DIR / "servicios").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "barberos").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "carousel").mkdir(parents=True, exist_ok=True)

app.mount(
    "/media/servicios",
    StaticFiles(directory=str(STATIC_DIR / "servicios")),
    name="media-servicios",
)

app.mount(
    "/media/barberos",
    StaticFiles(directory=str(STATIC_DIR / "barberos")),
    name="media-barberos",
)

app.mount(
    "/media/carousel",
    StaticFiles(directory=str(STATIC_DIR / "carousel")),
    name="media-carousel",
)

# =======================
# CORS (mismo criterio que ProyectoBurgers: CORS_ORIGINS + opcional CORS_ORIGIN_REGEX)
# Si el front abre desde otro host (dominio, IP LAN, túnel), el POST a /visitas/mercadopago/sincronizar
# falla en el navegador y la BD nunca se actualiza.
# =======================

_default_cors = (
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:4173,http://127.0.0.1:4173,"
    "http://192.168.1.62:5173,http://167.62.53.159:5173,"
    "http://167.62.232.17:5173,http://186.53.205.51:5173,http://179.27.203.212:5173,"
    "https://kingbarber.webhop.net,http://kingbarber.webhop.net"
)
_cors_raw = os.getenv("CORS_ORIGINS", _default_cors)
_cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]
_cors_regex_raw = os.getenv("CORS_ORIGIN_REGEX", "").strip()
_cors_origin_regex = _cors_regex_raw if _cors_regex_raw else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# ROUTERS
# =======================

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(barberos.router)
app.include_router(servicios.router)
app.include_router(horarios.router)
app.include_router(visitas.router)
app.include_router(admin.router)
app.include_router(perfil.router)
app.include_router(estadisticas.router)
app.include_router(carousel.router)
app.include_router(tv.router)

# =======================
# HEALTH CHECK
# =======================

@app.get("/")
def health():
    return {"status": "ok"}
