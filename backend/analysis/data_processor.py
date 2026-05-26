"""
🦄 Data Processor - Lidiando con la data SUCIA

Aquí es donde descubrís por qué el "data cleaning" es el 80% del trabajo.

El dataset tiene:
- Book_Details.csv: 16,225 libros (más o menos limpios)
- book_reviews.db: 63,014 reviews (SUCIAS. Muy sucias.)

La realidad de las reviews:
- Emojis raros: 🤪🎪👻🍆🔞 (sí, eso)
- Idiomas mezclados: "Great book! Me encantó 5/5 ⭐️ 很好"
- Bots: "5 stars" repetido 100 veces
- Nulls, vacías, caracteres especiales
- Spam, publicidad, reviews trolles

Tu misión:
1. Cargar dataset
2. Remover basura
3. Dejar reviews usables para BERT

Estimación realista:
- Entrada: 63,014 reviews
- Salida: ~55,000-60,000 (perdemos 5-12%)
- Es NORMAL. No es tu culpa.

Si pierdes el 50%+, algo está muy mal.
"""

import pandas as pd
import sqlite3
import os
from typing import Tuple
import re
from langdetect import detect, LangDetectException
from langdetect import DetectorFactory          
DetectorFactory.seed = 0 
# ============================================
# CONFIGURACIÓN
# ============================================

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data')
ARCHIVE_PATH = os.path.join(os.path.dirname(__file__), '../../archive')
BOOKS_CSV = os.path.join(DATA_PATH, 'Book_Details.csv')
REVIEWS_DB = os.path.join(ARCHIVE_PATH, 'book_reviews.db')

# ============================================
# FUNCIONES HELPER
# ============================================

def is_english(text: str) -> bool:
    if not isinstance(text, str) or len(text.strip()) < 5:
        return False
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False

def count_non_english_reviews(
    reviews_df: pd.DataFrame,
    text_column: str = "review_content"
) -> dict:
    """
    Cuenta cuántas reviews NO están en inglés.

    Returns:
        {
            "total_reviews": int,
            "english_reviews": int,
            "non_english_reviews": int,
            "non_english_percentage": float
        }
    """
    

    english_count = 0
    non_english_count = 0

    for text in reviews_df[text_column]:

        if not isinstance(text, str) or len(text.strip()) < 5:
            continue

        try:
            lang = detect(text)

            if lang == "en":
                english_count += 1
            else:
                non_english_count += 1

        except LangDetectException:
            # Textos raros/vacíos
            continue

    total = english_count + non_english_count

    percentage = (
        round((non_english_count / total) * 100, 2)
        if total > 0 else 0
    )

    return {
        "total_reviews": total,
        "english_reviews": english_count,
        "non_english_reviews": non_english_count,
        "non_english_percentage": percentage
    }
    
def get_unique_filename(base_name: str) -> str:
    """
    Genera un nombre de archivo único para evitar sobreescribir CSVs.

    Ejemplo:
    - books_clean.csv
    - books_clean_1.csv
    - books_clean_2.csv
    """
    if not os.path.exists(base_name):
        return base_name

    name, ext = os.path.splitext(base_name)
    counter = 1

    while True:
        new_name = f"{name}_{counter}{ext}"

        if not os.path.exists(new_name):
            return new_name

        counter += 1

def clean_text(text: str) -> str:
    """
    Limpia texto de review para procesamiento.

    Operaciones:
    - Convertir a minúsculas
    - Remover URLs
    - Remover caracteres especiales
    - Remover espacios múltiples
    - Remover emojis (opcional)

    Args:
        text: Texto crudo de review

    Returns:
        Texto limpio

    Nota:
        Los estudiantes pueden mejorar:
        - Traducir a inglés (BERT está entrenado en inglés)
        - Remover stopwords
        - Lemmatización/stemming
        - Manejo de emojis (a veces son informativos)
    """
    if not isinstance(text, str):
        return ""

    # Convertir a minúsculas
    text = text.lower()

    # Remover URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remover emojis
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remover espacios múltiples
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def validate_review(review_text: str, min_length: int = 10) -> bool:
    """
    Valida si una review es usable para análisis.

    Criterios:
    - No vacía
    - Longitud mínima (10 caracteres)
    - No es spam/bot

    Args:
        review_text: Texto de review
        min_length: Longitud mínima aceptada

    Returns:
        True si la review es válida

    Nota:
        Los estudiantes pueden mejorar:
        - Detectar spam/bots (reviews idénticas, patrones)
        - Detectar idioma (mantener solo inglés)
        - Score de relevancia
    """

    """
    Valida si una review es usable para análisis.
    """
    if not isinstance(review_text, str):
        return False

    text = review_text.strip()

    # No vacía / longitud mínima
    if len(text) < min_length:
        return False

    # Evitar reviews demasiado cortas tipo "5 stars"
    if text in ["5 stars", "4 stars", "3 stars", "2 stars", "1 star"]:
        return False

    # Evitar textos repetitivos tipo "good good good good good"
    words = text.split()
    if len(words) >= 5:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.4:
            return False

    # Evitar reviews con casi solo números
    letters = re.findall(r"[a-zA-Z]", text)
    if len(letters) < min_length:
        return False

    return True

def parse_review_rating(rating_text) -> float:
    """
    Convierte ratings tipo 'Rating 4 out of 5' a número.
    """
    if pd.isna(rating_text):
        return None

    rating_text = str(rating_text).strip()

    match = re.search(r'(\d+)\s+out of\s+5', rating_text, re.IGNORECASE)

    if match:
        return float(match.group(1))
    

def extract_publication_year(publication_info):
    """
    Extrae el año desde publication_info.
    """
    if pd.isna(publication_info):
        return None

    publication_info = str(publication_info)

    match = re.search(r'\b(19\d{2}|20\d{2})\b', publication_info)

    if match:
        return int(match.group(1))

    return None

    

# ============================================
# FUNCIONES PRINCIPALES
# ============================================

def load_dataset() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga el dataset completo (libros + reviews).

    Returns:
        Tuple: (books_df, reviews_df)

    books_df columns:
        - book_id
        - title
        - author
        - rating
        - publication_year
        - ...

    reviews_df columns:
        - review_id
        - book_id
        - review_text
        - rating
        - date
        - ...

    Raises:
        FileNotFoundError: Si no existen los archivos

    Nota:
        Los estudiantes deben:
        1. Explorar estructura del dataset
        2. Usar .head(), .info(), .describe()
        3. Identificar columnas relevantes
        4. Detectar valores nulos
    """
    # Cargar libros CSV
    books = pd.read_csv(BOOKS_CSV)
    # Convertir dato a datatime
    books["publication_year"] = books["publication_info"].apply(extract_publication_year).astype("Int64")
    # Guardar CSV SIN sobreescribir
    books_filename = get_unique_filename("books_clean.csv")
    books.to_csv(
        books_filename,
        index=False
    )

    print(f"Books guardado en: {books_filename}")

    # Cargar reviews desde SQLite
    conn = sqlite3.connect(REVIEWS_DB)
    reviews = pd.read_sql("SELECT * FROM book_reviews", conn)
    conn.close()

    return books, reviews



def preprocess_reviews(
    reviews_df: pd.DataFrame,
    min_review_length: int = 10
) -> pd.DataFrame:
    """
    Limpia y valida reviews.

    Operaciones:
    1. Remover filas con review_text nulo
    2. Limpiar texto (clean_text)
    3. Validar longitud mínima
    4. Remover duplicados

    Args:
        reviews_df: DataFrame con reviews crudas
        min_review_length: Longitud mínima de review

    Returns:
        DataFrame limpio

    Estadísticas esperadas:
        - Entrada: 63,014 reviews
        - Salida: ~55,000-60,000 reviews (después de limpiar)
        - Porcentaje de pérdida: ~5-12% (normal)

    Nota:
        Los estudiantes deben:
        1. Explorar qué se descarta (por qué?)
        2. Documentar cambios
        3. Considerar impacto en análisis
    """
    df = reviews_df.copy()

    # Validar longitud mínima
    df = df[df["review_content"].apply(lambda text: validate_review(text, min_review_length))]

    # Eliminar duplicados
    df = df.drop_duplicates(subset=["review_content"])

    # Limpiar texto
    df["review_content"] = df["review_content"].apply(clean_text)
    
    # Validar idioma inglés
    df = df[df["review_content"].apply(is_english)]
    
    # Validar longitud mínima
    df = df[df["review_content"].apply(lambda text: validate_review(text, min_review_length))]

    # Eliminar duplicados
    df = df.drop_duplicates(subset=["review_content"])

    # Limpiar rating de review
    if "review_rating" in df.columns:
     df["review_rating"] = df["review_rating"].apply(parse_review_rating)

    # Eliminar reviews sin rating válido
    df = df[df["review_rating"].notna()].copy()

    # Convertir a entero nullable de pandas
    df["review_rating"] = df["review_rating"].astype("Int64")
    return df



def get_book_stats(books_df: pd.DataFrame, reviews_df: pd.DataFrame) -> dict:
    """
    Calcula estadísticas del dataset.

    Returns:
        Dict con:
        - total_books
        - total_reviews
        - avg_reviews_per_book
        - date_range
        - rating_distribution
        - etc.

    Uso:
        Entender características del dataset
        Verificar que la carga fue correcta
    """
    return {
    "total_books": len(books_df),
    "total_reviews": len(reviews_df),
    "avg_reviews_per_book": round(len(reviews_df) / len(books_df), 2),
    "books_columns": books_df.columns.tolist(),
    "reviews_columns": reviews_df.columns.tolist()
}



# ============================================
# DEBUGGING / TESTING
# ============================================

if __name__ == "__main__":
    # Test local
    print("Cargando dataset...")
    books, reviews = load_dataset()

    print(f"Books shape: {books.shape}")
    print(f"Reviews shape: {reviews.shape}")
    print("\nBooks columns:", books.columns.tolist())
    print("\nReviews columns:", reviews.columns.tolist())

    print("\nLimpiando reviews...")
    reviews_clean = preprocess_reviews(reviews)
    reviews_filename = get_unique_filename("reviews_clean.csv")
    reviews_clean.to_csv(reviews_filename,index=False)

    print(f"Reviews guardado en: {reviews_filename}")
    print("\nReview rating limpio:")
    print(reviews_clean["review_rating"].head(10))
    print("Tipo:", reviews_clean["review_rating"].dtype)
    print("Valores únicos:", sorted(reviews_clean["review_rating"].dropna().unique()))
    print(f"Reviews después de limpiar: {reviews_clean.shape}")

    print("\nEstadísticas...")
    stats = get_book_stats(books, reviews_clean)
    print(stats)
    print("\nDetectando idiomas...")
    language_stats = count_non_english_reviews(reviews_clean)
    print(language_stats)