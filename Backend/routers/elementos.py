import re
import shutil
import unicodedata
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/elementos", tags=["Elementos"])

UPLOADS = Path(__file__).resolve().parent.parent / "uploads"
EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".webp"}
EXT_AUDIO = {".mp3", ".wav", ".ogg"}


# ---------- Utilidades ----------
def normalizar(texto: str) -> str:
    """'Árbol Grande' -> 'arbol_grande' (misma regla que tu app de escritorio)."""
    t = unicodedata.normalize("NFD", texto.strip().lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def limpiar(valor: Optional[str]) -> Optional[str]:
    """Swagger manda '' en campos vacíos; lo convertimos a None."""
    if valor is None:
        return None
    valor = valor.strip()
    return valor or None


def guardar_archivo(archivo: UploadFile, subcarpeta: str, nombre: str, permitidas: set) -> str:
    ext = Path(archivo.filename).suffix.lower()
    if ext not in permitidas:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{ext}' no permitido. Usa: {', '.join(sorted(permitidas))}",
        )
    carpeta = UPLOADS / subcarpeta
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / f"{nombre}{ext}"
    with destino.open("wb") as f:
        shutil.copyfileobj(archivo.file, f)
    return f"{subcarpeta}/{destino.name}"


def borrar_archivo(ruta: Optional[str]) -> None:
    if ruta:
        (UPLOADS / ruta).unlink(missing_ok=True)


def aplicar_archivo(elemento, campo, archivo, subcarpeta, sufijo, permitidas):
    """Guarda el archivo (si se envió) y reemplaza el anterior."""
    if archivo and archivo.filename:
        base = normalizar(elemento.nombre_espanol) + sufijo
        nueva = guardar_archivo(archivo, subcarpeta, base, permitidas)
        anterior = getattr(elemento, campo)
        if anterior and anterior != nueva:
            borrar_archivo(anterior)
        setattr(elemento, campo, nueva)


def obtener_o_404(db: Session, id: int) -> models.Elemento:
    elemento = db.query(models.Elemento).get(id)
    if not elemento:
        raise HTTPException(status_code=404, detail="Elemento no encontrado")
    return elemento


# ---------- Endpoints ----------
@router.get("", response_model=List[schemas.ElementoSalida])
def listar(
    categoria: Optional[str] = None,
    buscar: Optional[str] = None,
    db: Session = Depends(get_db),
):
    consulta = db.query(models.Elemento)
    if categoria:
        consulta = consulta.filter(models.Elemento.categoria == categoria)
    if buscar:
        patron = f"%{buscar}%"
        consulta = consulta.filter(
            or_(
                models.Elemento.nombre_espanol.like(patron),
                models.Elemento.nombre_mazahua.like(patron),
            )
        )
    return consulta.order_by(models.Elemento.id).all()


@router.get("/{id}", response_model=schemas.ElementoSalida)
def consultar(id: int, db: Session = Depends(get_db)):
    return obtener_o_404(db, id)


@router.post("", response_model=schemas.ElementoSalida, status_code=201)
def crear(
    nombre_espanol: str = Form(...),
    nombre_mazahua: str = Form(...),
    descripcion: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    uid_rfid: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    audio_mazahua: Optional[UploadFile] = File(None),
    audio_espanol: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    nombre_espanol = nombre_espanol.strip()
    if db.query(models.Elemento).filter(models.Elemento.nombre_espanol == nombre_espanol).first():
        raise HTTPException(status_code=409, detail="Ese elemento ya existe")

    elemento = models.Elemento(
        nombre_espanol=nombre_espanol,
        nombre_mazahua=nombre_mazahua.strip(),
        descripcion=limpiar(descripcion),
        categoria=limpiar(categoria),
        uid_rfid=limpiar(uid_rfid),   # None, no '' (la columna es UNIQUE)
    )
    aplicar_archivo(elemento, "imagen", imagen, "imagenes", "", EXT_IMAGEN)
    aplicar_archivo(elemento, "audio_mazahua", audio_mazahua, "audios", "_mazahua", EXT_AUDIO)
    aplicar_archivo(elemento, "audio_espanol", audio_espanol, "audios", "_espanol", EXT_AUDIO)

    db.add(elemento)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El UID RFID o el nombre ya están registrados")
    db.refresh(elemento)
    return elemento


@router.put("/{id}", response_model=schemas.ElementoSalida)
def modificar(
    id: int,
    nombre_espanol: Optional[str] = Form(None),
    nombre_mazahua: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    uid_rfid: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    audio_mazahua: Optional[UploadFile] = File(None),
    audio_espanol: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    elemento = obtener_o_404(db, id)

    nuevo_es = limpiar(nombre_espanol)
    if nuevo_es and nuevo_es != elemento.nombre_espanol:
        repetido = (
            db.query(models.Elemento)
            .filter(models.Elemento.nombre_espanol == nuevo_es, models.Elemento.id != id)
            .first()
        )
        if repetido:
            raise HTTPException(status_code=409, detail="Ya existe otro elemento con ese nombre")
        elemento.nombre_espanol = nuevo_es

    # Solo se cambian los campos que se enviaron
    for campo, valor in (
        ("nombre_mazahua", nombre_mazahua),
        ("descripcion", descripcion),
        ("categoria", categoria),
        ("uid_rfid", uid_rfid),
    ):
        valor = limpiar(valor)
        if valor is not None:
            setattr(elemento, campo, valor)

    aplicar_archivo(elemento, "imagen", imagen, "imagenes", "", EXT_IMAGEN)
    aplicar_archivo(elemento, "audio_mazahua", audio_mazahua, "audios", "_mazahua", EXT_AUDIO)
    aplicar_archivo(elemento, "audio_espanol", audio_espanol, "audios", "_espanol", EXT_AUDIO)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El UID RFID ya está registrado")
    db.refresh(elemento)
    return elemento


@router.delete("/{id}", status_code=204)
def eliminar(id: int, db: Session = Depends(get_db)):
    elemento = obtener_o_404(db, id)
    for ruta in (elemento.imagen, elemento.audio_mazahua, elemento.audio_espanol):
        borrar_archivo(ruta)
    db.delete(elemento)
    db.commit()