import os
from pathlib import Path

from dotenv import load_dotenv

# Path base del backend (donde está main.py)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
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
# CORS
# =======================
_base_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://localhost:5174",
    "https://127.0.0.1:5174",
]
# Producción / LAN: lista separada por comas, ej. https://app.midominio.com,https://www.midominio.com
_extra_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
_cors_origins = list(dict.fromkeys(_base_origins + _extra_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # Vite por IP/LAN/dominio en 5173 o 5174 (sin listar cada IP)
    allow_origin_regex=r"^https?://[^/]+:(5173|5174)$",
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
