from sqlalchemy import Column, Integer, String, Text

from database import Base


class Elemento(Base):
    __tablename__ = "elementos"

    id = Column(Integer, primary_key=True, index=True)
    nombre_espanol = Column(String(100), nullable=False)
    nombre_mazahua = Column(String(100), nullable=False)
    descripcion = Column(Text)
    categoria = Column(String(50))
    imagen = Column(String(255))
    audio_mazahua = Column(String(255))
    audio_espanol = Column(String(255))
    uid_rfid = Column(String(20), unique=True, nullable=True)