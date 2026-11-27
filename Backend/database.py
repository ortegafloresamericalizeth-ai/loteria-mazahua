import os
from urllib.parse import quote_plus

import certifi
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# En Render (TiDB): se define DATABASE_URL en las variables de entorno.
# En tu computadora: si no existe, usa MySQL local como antes.
DATABASE_URL = os.getenv("mysql+pymysql://2mTTSp8sRRvfx9w.root:fzVJeaPEcG34iRtA@gateway01.us-east-1.prod.aws.tidbcloud.com:4000/loteria_mazahua?charset=utf8mb4")

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"ssl": {"ca": certifi.where()}},
    )
else:
    USUARIO = "2mTTSp8sRRvfx9w.root"
    PASSWORD = os.getenv("LOTERIA_DB_PASSWORD", "fzVJeaPEcG34iRtA")
    HOST = "gateway01.us-east-1.prod.aws.tidbcloud.com"
    BD = "loteria_mazahua"
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