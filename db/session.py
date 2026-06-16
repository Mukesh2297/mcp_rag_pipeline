from core.config import settings
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_DATABASE = settings.DB_DATABASE
DB_USERNAME = settings.DB_USERNAME
DB_PASSWORD = settings.DB_PASSWORD

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT) if DB_PORT else None,
    database=DB_DATABASE,
)

print(f"constructed db url is {database_url.render_as_string(hide_password=True)}")

engine = create_engine(
    url=database_url,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass



def init_db():
    from models import Document

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        conn.execute(
            text(
                "ALTER TABLE IF EXISTS documents "
                "ALTER COLUMN embedding TYPE vector(768)"
            )
        )
        conn.commit()

    print("Database connection established")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
