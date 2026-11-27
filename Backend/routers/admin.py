import hashlib
import hmac
import os
import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Docente, Partida, Sesion

router = APIRouter(prefix="/api")

# Opcional: si defines CODIGO_REGISTRO, solo se registra quien lo conozca
CODIGO_REGISTRO = os.getenv("CODIGO_REGISTRO", "")
DIAS_SESION = 7
CORREO_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Contraseñas ----------
def hashear(clave: str) -> str:
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, 200_000)
    return f"{sal.hex()}${h.hex()}"


def verificar(clave: str, guardado: str) -> bool:
    try:
        sal_hex, h_hex = guardado.split("$")
        nuevo = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal_hex), 200_000)
    except ValueError:
        return False
    return hmac.compare_digest(nuevo.hex(), h_hex)


# ---------- Esquemas ----------
class Registro(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: str = Field(max_length=120)
    password: str = Field(min_length=8, max_length=100)
    codigo: str = ""


class Login(BaseModel):
    correo: str
    password: str


class NuevaPartida(BaseModel):
    tableros: int = Field(ge=1, le=40)
    cartas_por_tablero: int


# ---------- Sesión ----------
def crear_sesion(db: Session, docente: Docente) -> str:
    token = secrets.token_urlsafe(32)
    db.add(Sesion(token=token, docente_id=docente.id))
    db.commit()
    return token


def token_de(authorization: Optional[str]) -> str:
    return (authorization or "").removeprefix("Bearer ").strip()


def docente_actual(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Docente:
    ses = db.get(Sesion, token_de(authorization))
    if not ses or ses.creado < datetime.utcnow() - timedelta(days=DIAS_SESION):
        raise HTTPException(status_code=401, detail="Sesión no válida")
    docente = db.get(Docente, ses.docente_id)
    if not docente:
        raise HTTPException(status_code=401, detail="Sesión no válida")
    return docente


# ---------- Cuenta ----------
@router.post("/admin/registro")
def registrar(datos: Registro, db: Session = Depends(get_db)):
    if CODIGO_REGISTRO and not secrets.compare_digest(datos.codigo, CODIGO_REGISTRO):
        raise HTTPException(status_code=403, detail="Código de docente incorrecto")

    correo = datos.correo.strip().lower()
    if not CORREO_RE.match(correo):
        raise HTTPException(status_code=400, detail="Escribe un correo válido")
    if db.query(Docente).filter(Docente.correo == correo).first():
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado")

    docente = Docente(nombre=datos.nombre.strip(), correo=correo, clave_hash=hashear(datos.password))
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return {"token": crear_sesion(db, docente), "nombre": docente.nombre}


@router.post("/admin/login")
def login(datos: Login, db: Session = Depends(get_db)):
    docente = db.query(Docente).filter(Docente.correo == datos.correo.strip().lower()).first()
    if not docente or not verificar(datos.password, docente.clave_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    return {"token": crear_sesion(db, docente), "nombre": docente.nombre}


@router.get("/admin/yo")
def yo(docente: Docente = Depends(docente_actual)):
    return {"nombre": docente.nombre, "correo": docente.correo}


@router.post("/admin/salir")
def salir(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    ses = db.get(Sesion, token_de(authorization))
    if ses:
        db.delete(ses)
        db.commit()
    return {"ok": True}


# ---------- Partidas del docente ----------
def a_dict(p: Partida) -> dict:
    return {
        "codigo": p.codigo,
        "tableros": p.tableros,
        "cartas_por_tablero": p.cartas_por_tablero,
        "creado": p.creado.isoformat() if p.creado else None,
    }


@router.get("/admin/partidas")
def mis_partidas(docente: Docente = Depends(docente_actual), db: Session = Depends(get_db)):
    lista = (
        db.query(Partida)
        .filter(Partida.docente_id == docente.id)
        .order_by(Partida.creado.desc())
        .all()
    )
    return [a_dict(p) for p in lista]


@router.post("/admin/partidas")
def crear_partida(
    datos: NuevaPartida,
    docente: Docente = Depends(docente_actual),
    db: Session = Depends(get_db),
):
    if datos.cartas_por_tablero not in (9, 16):
        raise HTTPException(status_code=400, detail="Las cartas por tablero deben ser 9 o 16")

    alfabeto = string.ascii_uppercase + string.digits
    while True:
        codigo = "".join(secrets.choice(alfabeto) for _ in range(5))
        if not db.query(Partida).filter(Partida.codigo == codigo).first():
            break

    partida = Partida(
        codigo=codigo,
        docente_id=docente.id,
        tableros=datos.tableros,
        cartas_por_tablero=datos.cartas_por_tablero,
    )
    db.add(partida)
    db.commit()
    db.refresh(partida)
    return a_dict(partida)


@router.delete("/admin/partidas/{codigo}")
def borrar_partida(
    codigo: str,
    docente: Docente = Depends(docente_actual),
    db: Session = Depends(get_db),
):
    partida = (
        db.query(Partida)
        .filter(Partida.codigo == codigo.upper(), Partida.docente_id == docente.id)
        .first()
    )
    if not partida:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    db.delete(partida)
    db.commit()
    return {"ok": True}


# ---------- Pública: los jugadores consultan por código ----------
@router.get("/partidas/{codigo}")
def ver_partida(codigo: str, db: Session = Depends(get_db)):
    partida = db.query(Partida).filter(Partida.codigo == codigo.upper()).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Código no encontrado")
    return a_dict(partida)