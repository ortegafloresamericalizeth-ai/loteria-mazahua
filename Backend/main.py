from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import models
from database import engine
from routers import elementos, juego
from routers.admin import router as admin_router

BASE = Path(__file__).resolve().parent
for sub in ("imagenes", "audios"):
    (BASE / "uploads" / sub).mkdir(parents=True, exist_ok=True)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lotería Interactiva Mazahua", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://127.0.0.1:4321"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sirve imágenes y audios: http://127.0.0.1:8000/uploads/imagenes/perro.png
app.mount("/uploads", StaticFiles(directory=BASE / "uploads"), name="uploads")

app.include_router(elementos.router)
app.include_router(juego.router)
app.include_router(admin_router)