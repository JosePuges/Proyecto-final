"""
🦄 DATABASE - Conexión a la Base de Datos
El unicornio que guarda todos tus libros y usuarios con magia SQLAlchemy ✨
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 🦄 SQLite para desarrollo local (sin Docker, sin líos)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./libros.db")

# 🔧 El motor que mueve la magia
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 📦 La fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🏗️ Crea las tablas automáticamente si no existen
Base.metadata.create_all(bind=engine)


def get_db():
    """🎁 Le da a FastAPI una sesión de BD fresquita en cada request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()