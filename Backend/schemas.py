from typing import Optional

from pydantic import BaseModel, ConfigDict


class ElementoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_espanol: str
    nombre_mazahua: str
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    imagen: Optional[str] = None
    audio_mazahua: Optional[str] = None
    audio_espanol: Optional[str] = None
    uid_rfid: Optional[str] = None