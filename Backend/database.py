import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

USUARIO = "root"
PASSWORD = os.getenv("LOTERIA_DB_PASSWORD", "123456")
HOST = "localhost"
BD = "loteria_mazahua"

# quote_plus evita problemas si la contraseña tiene símbolos como @ o #
URL = f"mysql+pymysql://{USUARIO}:{quote_plus(PASSWORD)}@{HOST}/{BD}?charset=utf8mb4"

engine = create_engine(URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()