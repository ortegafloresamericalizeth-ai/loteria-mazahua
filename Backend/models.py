
from sqlalchemy import Column, Integer, String, Text
from datetime import datetime
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

    from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String


class Docente(Base):
    __tablename__ = "docentes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)
    correo = Column(String(120), unique=True, index=True, nullable=False)
    clave_hash = Column(String(200), nullable=False)
    creado = Column(DateTime, default=datetime.utcnow)


class Sesion(Base):
    __tablename__ = "sesiones"

    token = Column(String(64), primary_key=True)
    docente_id = Column(Integer, ForeignKey("docentes.id"), nullable=False, index=True)
    creado = Column(DateTime, default=datetime.utcnow)


class Partida(Base):
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(8), unique=True, index=True, nullable=False)
    docente_id = Column(Integer, ForeignKey("docentes.id"), nullable=False, index=True)
    tableros = Column(Integer, nullable=False)
    cartas_por_tablero = Column(Integer, nullable=False)
    creado = Column(DateTime, default=datetime.utcnow)