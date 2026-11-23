import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/juego", tags=["Juego"])


@router.get("/baraja", response_model=List[schemas.ElementoSalida])
def baraja(db: Session = Depends(get_db)):
    """Todas las cartas en orden aleatorio (para ir 'cantándolas')."""
    cartas = db.query(models.Elemento).all()
    random.shuffle(cartas)
    return cartas


@router.get("/tablero", response_model=List[schemas.ElementoSalida])
def tablero(tamano: int = Query(16, ge=4, le=25), db: Session = Depends(get_db)):
    """Tablero de un jugador: 'tamano' cartas distintas al azar."""
    cartas = db.query(models.Elemento).all()
    if len(cartas) < tamano:
        raise HTTPException(
            status_code=400,
            detail="No hay suficientes elementos para el tablero",
        )
    return random.sample(cartas, tamano)