"""
🦄 MODELS - Las Tablas de la Base de Datos
El unicornio que organiza dónde vive cada dato ✨
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """🧑 Tabla: users - Quién se loguea"""
    __tablename__ = "users"

    email = Column(String, primary_key=True, unique=True, nullable=False)
    username = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(email={self.email}, username={self.username})>"

class UserReview(Base):
    """📖 Tabla: user_reviews - Reviews que dejan los usuarios"""
    __tablename__ = "user_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    book_title = Column(String, nullable=False)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserReview(book={self.book_title}, user={self.user_email})>"