"""
🦄 SCHEMAS - Modelos Pydantic para Validación

Pydantic valida que los datos que llegan en las requests sean del tipo correcto.

Ejemplo:
- Usuario envía: {"email": "test@test.com", "password": "123456"}
- Pydantic verifica: ¿email es string? ¿password es string?
- Si falta algo o es del tipo incorrecto → 422 Unprocessable Entity
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    """
    Request: POST /auth/register

    Body:
    {
        "email": "alumno@test.com",
        "password": "securepassword123"
    }
    """
  
    email: str
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    """
    Request: POST /auth/login

    Body:
    {
        "email": "alumno@test.com",
        "password": "securepassword123"
    }
    """
    email: str
    password: str


class UserFeedback(BaseModel):
    """
    Request: POST /user/feedback

    Body:
    {
        "book_title": "The Midnight Library",
        "review_text": "Me encantó mucho, cambió mi perspectiva",
        "rating": 5
    }
    """
    book_title: str
    review_text: str
    rating: int  # XXX TODO: Validar que sea 1-5 (Field(ge=1, le=5))


class TokenResponse(BaseModel):
    """
    Response: POST /auth/register o /auth/login

    Body:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer"
    }
    """
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """
    Response: GET /user/me

    Body:
    {
        "email": "alumno@test.com"
    }
    """
    email: str


class ReviewResponse(BaseModel):
    """
    Respuesta individual de una review
    """
    book_title: str
    review_text: str
    rating: int
    created_at: str


class HistoryResponse(BaseModel):
    """
    Response: GET /user/history

    Body:
    {
        "email": "alumno@test.com",
        "reviews": [
            {
                "book_title": "The Midnight Library",
                "review_text": "Me encantó",
                "rating": 5,
                "created_at": "2026-05-19T10:30:00"
            }
        ]
    }
    """
    email: str
    reviews: list[ReviewResponse]


class AddNewBook(BaseModel):
    """
    Request: POST /book/add-with-review

    Cuando usuario quiere añadir un libro que no existe,
    lo hace junto con su reseña.

    Body:
    {
        "book_title": "Cien años de soledad",
        "author": "Gabriel García Márquez",
        "cover_image_uri": "https://...",
        "genres": "Realismo Mágico, Ficción",
        "review_content": "Una obra maestra...",
        "review_rating": 5
    }
    """
    book_title: str
    author: str
    cover_image_uri: Optional[str] = None
    genres: Optional[str] = None
    review_content: str
    review_rating: int  # XXX TODO: Validar 1-5


class BookNotFoundResponse(BaseModel):
    """
    Response: POST /recommend (libro no encontrado)

    {
        "error": "Book not found",
        "suggestion": "Would you like to add it with your review?",
        "book_title": "Harry Potter"
    }
    """
    error: str
    suggestion: str
    book_title: str


class UpdateUsername(BaseModel):
    username: str

class UpdatePassword(BaseModel):
    current_password: str
    new_password: str


# ============================================
# XXX VALIDACIONES EXTRAS (PARA DESPUÉS)
# ============================================

# Si quieren validar más estrictamente:
# from pydantic import Field, validator

# class UserRegister(BaseModel):
#     email: EmailStr  # Valida que sea email real
#     password: str = Field(..., min_length=8)  # Mínimo 8 caracteres

# class UserFeedback(BaseModel):
#     book_title: str = Field(..., min_length=1)
#     review_text: str = Field(..., min_length=10)  # Mínimo 10 caracteres
#     rating: int = Field(..., ge=1, le=5)  # Entre 1 y 5

#     @validator('review_text')
#     def review_not_spam(cls, v):
#         if len(set(v.split())) < 3:  # Al menos 3 palabras únicas
#             raise ValueError('Review muy corta o spam')
#         return v
