from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    clientes,
    barberos,
    visitas,
    horarios,
    servicios,
    auth
)

app = FastAPI(
    title="API Barbería",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(barberos.router)
app.include_router(servicios.router)
app.include_router(horarios.router)
app.include_router(visitas.router)

@app.get("/")
def health():
    return {"status": "ok"}
