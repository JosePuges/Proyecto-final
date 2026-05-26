from pathlib import Path
from dotenv import load_dotenv
import sys
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from analysis.recommender import recomendar_por_afinidad_emocional, find_similar_books
from analysis.cache_manager import CacheManager, cache_sentiment
from auth import hash_password, verify_password, create_access_token, verify_token
from database import get_db
from schemas import UserRegister, UserLogin, TokenResponse, UserFeedback, UpdateUsername, UpdatePassword
from models import User, UserReview

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = ROOT_DIR / "data"

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# ============================================================
# ARCHIVOS CSV
# ============================================================

BOOKS_PATH = DATA_DIR / "books_clean.csv"
PROFILES_PATH = DATA_DIR / "emotion_profiles.csv"
RECOMMENDATIONS_PATH = DATA_DIR / "all_book_recommendations.csv"

# ============================================================
# APP FASTAPI
# ============================================================

app = FastAPI(
    title="API Recomendador de Libros",
    description="API para buscar libros y recomendar por afinidad emocional.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CACHE
# ============================================================

cache = CacheManager()
books_df = None
profiles_df = None
recommendations_df = None


def cargar_csv_seguro(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    return pd.read_csv(path)


def get_books_df() -> pd.DataFrame:
    global books_df
    if books_df is None:
        books_df = cargar_csv_seguro(BOOKS_PATH)
    return books_df


def get_profiles_df() -> pd.DataFrame:
    global profiles_df
    if profiles_df is None:
        profiles_df = cargar_csv_seguro(PROFILES_PATH)
    return profiles_df


def get_recommendations_df() -> pd.DataFrame:
    global recommendations_df
    if recommendations_df is None:
        recommendations_df = cargar_csv_seguro(RECOMMENDATIONS_PATH)
    return recommendations_df


def limpiar_nan(valor):
    if pd.isna(valor):
        return None
    if hasattr(valor, "item"):
        return valor.item()
    return valor


def fila_a_dict(fila) -> dict:
    return {columna: limpiar_nan(valor) for columna, valor in fila.items()}


def normalizar_texto(texto) -> str:
    if texto is None:
        return ""
    return str(texto).lower().strip()


# ============================================================
# HOME / HEALTH
# ============================================================

@app.get("/")
def home():
    return {
        "message": "API de recomendacion de libros funcionando correctamente",
        "version": "3.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "api": "ok",
        "data_dir": str(DATA_DIR),
        "books_clean.csv": BOOKS_PATH.exists(),
        "emotion_profiles.csv": PROFILES_PATH.exists(),
        "all_book_recommendations.csv": RECOMMENDATIONS_PATH.exists(),
    }


# ============================================================
# BOOKS
# ============================================================

@app.get("/books")
def listar_libros(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    try:
        df = get_books_df()
        total = len(df)
        resultados = df.iloc[offset:offset + limit]
        return {"total": total, "limit": limit, "offset": offset,
                "books": [fila_a_dict(fila) for _, fila in resultados.iterrows()]}
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/books/{book_id}")
def obtener_libro(book_id: str):
    try:
        df = get_books_df()
        df = df.copy()
        df["book_id"] = df["book_id"].astype(str)
        resultado = df[df["book_id"] == str(book_id)]
        if resultado.empty:
            raise HTTPException(status_code=404, detail=f"No se encontro el libro con book_id: {book_id}")
        return fila_a_dict(resultado.iloc[0])
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/search")
def buscar_libros(title: str = Query(..., min_length=1), limit: int = Query(default=10, ge=1, le=50)):
    try:
        df = get_books_df()
        df = df.copy()
        df["book_title"] = df["book_title"].fillna("").astype(str)
        resultados = df[df["book_title"].str.lower().str.contains(title.lower(), na=False, regex=False)].head(limit)
        return {"query": title, "total": len(resultados),
                "books": [fila_a_dict(fila) for _, fila in resultados.iterrows()]}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# EMOTION PROFILES
# ============================================================

@app.get("/profiles")
def listar_perfiles(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    try:
        df = get_profiles_df()
        total = len(df)
        resultados = df.iloc[offset:offset + limit]
        return {"total": total, "limit": limit, "offset": offset,
                "profiles": [fila_a_dict(fila) for _, fila in resultados.iterrows()]}
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/profiles/{book_id}")
def obtener_perfil_libro(book_id: str):
    try:
        df = get_profiles_df()
        df = df.copy()
        df["book_id"] = df["book_id"].astype(str)
        resultado = df[df["book_id"] == str(book_id)]
        if resultado.empty:
            raise HTTPException(status_code=404, detail=f"No se encontro perfil emocional para book_id: {book_id}")
        return fila_a_dict(resultado.iloc[0])
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/profiles/search/by-title")
def buscar_perfil_por_titulo(title: str = Query(..., min_length=1), limit: int = Query(default=10, ge=1, le=50)):
    try:
        df = get_profiles_df()
        df = df.copy()
        df["book_title"] = df["book_title"].fillna("").astype(str)
        resultados = df[df["book_title"].str.lower().str.contains(title.lower(), na=False, regex=False)].head(limit)
        return {"query": title, "total": len(resultados),
                "profiles": [fila_a_dict(fila) for _, fila in resultados.iterrows()]}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# RECOMENDACIONES
# ============================================================

@app.get("/recommendations/emotional")
def recomendar_emocional(
    title: str = Query(..., min_length=1),
    top_n: int = Query(default=5, ge=1, le=20),
    min_reviews: int = Query(default=1, ge=1),
    excluir_mismo_autor: bool = Query(default=False),
):
    """Recomendacion usando emotion_profiles.csv. No recalcula BERT ni lee reviews."""
    try:
        resultado = recomendar_por_afinidad_emocional(
            titulo_libro=title, top_n=top_n,
            min_reviews=min_reviews, excluir_mismo_autor=excluir_mismo_autor,
        )
        if "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return resultado
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/recommend")
def recomendar_compatibilidad(title: str = Query(..., min_length=1), num_recommendations: int = Query(default=5, ge=1, le=20)):
    """Endpoint compatible con versiones anteriores."""
    try:
        return find_similar_books(title=title, num_recommendations=num_recommendations)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/recommendations/precomputed")
def recomendaciones_precalculadas(
    book_id: Optional[str] = Query(default=None),
    title: Optional[str] = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
):
    """Lee all_book_recommendations.csv generado por recommender.py."""
    try:
        df = get_recommendations_df()
        df = df.copy()
        if book_id is not None:
            df["book_id"] = df["book_id"].astype(str)
            df = df[df["book_id"] == str(book_id)]
        elif title is not None:
            df["book_title"] = df["book_title"].fillna("").astype(str)
            df = df[df["book_title"].str.lower().str.contains(title.lower(), na=False, regex=False)]
        else:
            raise HTTPException(status_code=400, detail="Debes enviar book_id o title")
        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron recomendaciones precalculadas")
        if "recommended_rank" in df.columns:
            df = df.sort_values("recommended_rank")
        df = df.head(limit)
        return {"total": len(df), "recommendations": [fila_a_dict(fila) for _, fila in df.iterrows()]}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/reload")
def recargar_datos():
    """Limpia la cache en memoria. Util despues de cambiar CSVs."""
    global books_df, profiles_df, recommendations_df
    books_df = None
    profiles_df = None
    recommendations_df = None
    return {"message": "Datos recargados correctamente"}


# ============================================================
# AUTH ENDPOINTS
# ============================================================

def get_current_user(authorization: str = Header(..., alias="Authorization")) -> str:
    """Middleware que comprueba el token en cada request protegido"""
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401)
        email = verify_token(token)
        if not email:
            raise HTTPException(status_code=401)
        return email
    except:
        raise HTTPException(status_code=401, detail="Token invalido")


@app.post("/auth/register", response_model=TokenResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Registra un usuario nuevo"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    new_user = User(email=user.email, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Loguea un usuario existente"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/user/me")
def get_me(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """🦄 Devuelve los datos del usuario logueado"""
    user = db.query(User).filter(User.email == current_user).first()
    return {
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

@app.post("/user/feedback")
def save_feedback(feedback: UserFeedback, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Guarda una review de un usuario"""
    review = UserReview(
        user_email=current_user,
        book_title=feedback.book_title,
        review_text=feedback.review_text,
        rating=feedback.rating
    )
    db.add(review)
    db.commit()
    return {"status": "saved", "review_id": review.id}

@app.patch("/user/username")
def update_username(data: UpdateUsername, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """🦄 Cambia el nombre de usuario"""
    user = db.query(User).filter(User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.username = data.username
    db.commit()
    return {"status": "ok", "username": user.username}


@app.patch("/user/password")
def update_password(data: UpdatePassword, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """🦄 Cambia la contraseña"""
    user = db.query(User).filter(User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"status": "ok"}
# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando API de Recomendacion de Libros...")
    logger.info("Frontend: http://localhost:3000")
    logger.info("API: http://localhost:8000")
    logger.info("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)