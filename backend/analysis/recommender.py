from pathlib import Path
import ast
import re
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
DATA_DIR = ROOT_DIR / "data"

EMOTION_PROFILES_PATH = DATA_DIR / "emotion_profiles.csv"
BOOKS_PATH = DATA_DIR / "books_clean.csv"
OUTPUT_RECOMMENDATIONS_PATH = DATA_DIR / "all_book_recommendations.csv"


# ============================================================
# CONFIGURACIÓN DE SCORING
# ============================================================

EMOTION_COLUMNS = [
    "joy",
    "sadness",
    "fear",
    "surprise",
    "anger",
    "disgust",
    "average_sentiment",
]

BASIC_EMOTION_COLUMNS = [
    "joy",
    "sadness",
    "fear",
    "surprise",
    "anger",
    "disgust",
]

EMOTION_WEIGHT = 0.70
GENRE_WEIGHT = 0.20
RATING_WEIGHT = 0.07
AUTHOR_PENALTY_WEIGHT = 0.03


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_texto(texto):
    if texto is None or pd.isna(texto):
        return ""

    texto = str(texto).lower().strip()
    texto = re.sub(r"\s+", " ", texto)

    return texto


def texto_seguro(valor):
    if valor is None or pd.isna(valor):
        return ""

    return str(valor).strip()


def parsear_generos(valor):
    if valor is None or pd.isna(valor):
        return set()

    texto = str(valor).strip()

    if texto == "":
        return set()

    try:
        posible_lista = ast.literal_eval(texto)

        if isinstance(posible_lista, list):
            return {
                normalizar_texto(genero)
                for genero in posible_lista
                if normalizar_texto(genero) != ""
            }
    except Exception:
        pass

    partes = re.split(r"[,\|;/]", texto)

    return {
        normalizar_texto(parte)
        for parte in partes
        if normalizar_texto(parte) != ""
    }


def calcular_jaccard_generos(generos_a, generos_b):
    set_a = parsear_generos(generos_a)
    set_b = parsear_generos(generos_b)

    if not set_a or not set_b:
        return 0.0

    union = set_a.union(set_b)

    if not union:
        return 0.0

    return len(set_a.intersection(set_b)) / len(union)


def normalizar_rating(valor):
    try:
        rating = float(valor)
    except Exception:
        return 0.0

    if pd.isna(rating):
        return 0.0

    return max(0.0, min(rating / 5.0, 1.0))


def emocion_dominante(fila):
    valores = {}

    for columna in BASIC_EMOTION_COLUMNS:
        try:
            valores[columna] = float(fila.get(columna, 0.0))
        except Exception:
            valores[columna] = 0.0

    return max(valores, key=valores.get)


def traducir_emocion(emocion):
    mapa = {
        "joy": "Alegría",
        "sadness": "Tristeza",
        "fear": "Miedo",
        "surprise": "Sorpresa",
        "anger": "Ira",
        "disgust": "Asco",
    }

    return mapa.get(emocion, emocion)


def recortar_texto(texto, max_chars=900):
    texto = texto_seguro(texto)

    if len(texto) <= max_chars:
        return texto

    return texto[:max_chars].rstrip() + "..."


# ============================================================
# CARGA DE DATOS
# ============================================================

def cargar_perfiles_emocionales():
    if not EMOTION_PROFILES_PATH.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {EMOTION_PROFILES_PATH}. "
            "Copia emotion_profiles.csv dentro de /app/data/"
        )

    perfiles = pd.read_csv(EMOTION_PROFILES_PATH)

    columnas_necesarias = [
        "book_id",
        "book_title",
        "author",
    ] + EMOTION_COLUMNS

    for columna in columnas_necesarias:
        if columna not in perfiles.columns:
            raise ValueError(
                f"Falta la columna obligatoria '{columna}' en {EMOTION_PROFILES_PATH}"
            )

    perfiles = perfiles.copy()

    perfiles["book_id"] = perfiles["book_id"].astype(str).str.strip()
    perfiles["book_title"] = perfiles["book_title"].astype(str).str.strip()
    perfiles["author"] = perfiles["author"].fillna("Autor desconocido").astype(str)

    for columna in EMOTION_COLUMNS:
        perfiles[columna] = pd.to_numeric(perfiles[columna], errors="coerce")

    perfiles = perfiles.dropna(
        subset=["book_id", "book_title"] + EMOTION_COLUMNS
    ).copy()

    perfiles = perfiles[perfiles["book_id"] != ""]
    perfiles = perfiles[perfiles["book_title"] != ""]

    perfiles = perfiles.drop_duplicates(subset=["book_id"])

    return perfiles


def cargar_books_metadata():
    if not BOOKS_PATH.exists():
        print(f"⚠️ No existe {BOOKS_PATH}. Se recomendará solo con emociones.")
        return pd.DataFrame(
            columns=[
                "book_id",
                "genres",
                "average_rating",
                "language",
                "book_details",
            ]
        )

    books = pd.read_csv(BOOKS_PATH)

    if "book_id" not in books.columns:
        print("⚠️ books_clean.csv no tiene book_id. Se recomendará solo con emociones.")
        return pd.DataFrame(
            columns=[
                "book_id",
                "genres",
                "average_rating",
                "language",
                "book_details",
            ]
        )

    columnas_utiles = [
        "book_id",
        "genres",
        "average_rating",
        "language",
        "book_details",
    ]

    columnas_existentes = [
        columna
        for columna in columnas_utiles
        if columna in books.columns
    ]

    books = books[columnas_existentes].copy()
    books["book_id"] = books["book_id"].astype(str).str.strip()

    if "genres" not in books.columns:
        books["genres"] = ""

    if "average_rating" not in books.columns:
        books["average_rating"] = 0.0

    if "language" not in books.columns:
        books["language"] = ""

    if "book_details" not in books.columns:
        books["book_details"] = ""

    books["genres"] = books["genres"].fillna("").astype(str)
    books["language"] = books["language"].fillna("").astype(str)
    books["book_details"] = books["book_details"].fillna("").astype(str)

    books["average_rating"] = pd.to_numeric(
        books["average_rating"],
        errors="coerce",
    ).fillna(0.0)

    books = books.drop_duplicates(subset=["book_id"])

    return books


def cargar_perfiles():
    perfiles = cargar_perfiles_emocionales()
    books = cargar_books_metadata()

    if not books.empty:
        perfiles = perfiles.merge(
            books,
            on="book_id",
            how="left",
            suffixes=("", "_book"),
        )

    for columna in ["genres", "language", "book_details"]:
        if columna not in perfiles.columns:
            perfiles[columna] = ""

        perfiles[columna] = perfiles[columna].fillna("").astype(str)

    if "average_rating" not in perfiles.columns:
        perfiles["average_rating"] = 0.0

    perfiles["average_rating"] = pd.to_numeric(
        perfiles["average_rating"],
        errors="coerce",
    ).fillna(0.0)

    perfiles["emocion_dominante"] = perfiles.apply(emocion_dominante, axis=1)
    perfiles["emocion_dominante_es"] = perfiles["emocion_dominante"].apply(
        traducir_emocion
    )

    return perfiles


# ============================================================
# BÚSQUEDA DE LIBRO
# ============================================================

def buscar_libro_por_titulo(perfiles, titulo):
    titulo_normalizado = normalizar_texto(titulo)

    if titulo_normalizado == "":
        return None

    perfiles = perfiles.copy()
    perfiles["titulo_normalizado"] = perfiles["book_title"].apply(normalizar_texto)

    coincidencia_exacta = perfiles[
        perfiles["titulo_normalizado"] == titulo_normalizado
    ]

    if not coincidencia_exacta.empty:
        return coincidencia_exacta.sort_values(
            by=["average_rating"],
            ascending=False,
        ).iloc[0]

    coincidencia_parcial = perfiles[
        perfiles["titulo_normalizado"].str.contains(
            titulo_normalizado,
            na=False,
            regex=False,
        )
    ]

    if not coincidencia_parcial.empty:
        return coincidencia_parcial.sort_values(
            by=["average_rating"],
            ascending=False,
        ).iloc[0]

    palabras = [
        palabra
        for palabra in titulo_normalizado.split()
        if len(palabra) > 2
    ]

    if palabras:
        def contiene_palabras(titulo_fila):
            return all(palabra in titulo_fila for palabra in palabras[:3])

        coincidencia_palabras = perfiles[
            perfiles["titulo_normalizado"].apply(contiene_palabras)
        ]

        if not coincidencia_palabras.empty:
            return coincidencia_palabras.sort_values(
                by=["average_rating"],
                ascending=False,
            ).iloc[0]

    return None


def obtener_sugerencias_titulo(perfiles, titulo, limit=10):
    titulo_normalizado = normalizar_texto(titulo)

    if titulo_normalizado == "":
        return []

    palabras = [
        palabra
        for palabra in titulo_normalizado.split()
        if len(palabra) > 2
    ]

    if not palabras:
        return []

    primera_palabra = palabras[0]

    sugerencias = perfiles[
        perfiles["book_title"]
        .astype(str)
        .str.lower()
        .str.contains(primera_palabra, na=False, regex=False)
    ].copy()

    sugerencias = sugerencias.sort_values(
        by=["average_rating"],
        ascending=False,
    ).head(limit)

    columnas = [
        "book_id",
        "book_title",
        "author",
        "genres",
        "average_rating",
        "emocion_dominante_es",
    ]

    columnas = [
        columna
        for columna in columnas
        if columna in sugerencias.columns
    ]

    return sugerencias[columnas].to_dict(orient="records")


# ============================================================
# SCORING
# ============================================================

def calcular_scores(perfiles, libro_base):
    perfiles = perfiles.copy()

    matriz_features = perfiles[EMOTION_COLUMNS].astype(float)

    vector_libro_base = pd.DataFrame(
        [libro_base[EMOTION_COLUMNS].astype(float).values],
        columns=EMOTION_COLUMNS,
    )

    perfiles["emotion_similarity"] = cosine_similarity(
        vector_libro_base,
        matriz_features,
    )[0]

    generos_base = libro_base.get("genres", "")
    autor_base = normalizar_texto(libro_base.get("author", ""))

    perfiles["genre_similarity"] = perfiles["genres"].apply(
        lambda generos: calcular_jaccard_generos(generos_base, generos)
    )

    perfiles["rating_score"] = perfiles["average_rating"].apply(normalizar_rating)

    perfiles["same_author"] = perfiles["author"].apply(
        lambda autor: normalizar_texto(autor) == autor_base
    )

    perfiles["author_penalty"] = perfiles["same_author"].apply(
        lambda mismo_autor: 1.0 if mismo_autor else 0.0
    )

    perfiles["score_final"] = (
        perfiles["emotion_similarity"] * EMOTION_WEIGHT
        + perfiles["genre_similarity"] * GENRE_WEIGHT
        + perfiles["rating_score"] * RATING_WEIGHT
        - perfiles["author_penalty"] * AUTHOR_PENALTY_WEIGHT
    )

    perfiles["score_final"] = perfiles["score_final"].clip(
        lower=0.0,
        upper=1.0,
    )

    perfiles["similarity"] = perfiles["score_final"]

    return perfiles


# ============================================================
# CONSTRUCCIÓN DE RESPUESTAS
# ============================================================

def construir_libro_base(fila):
    return {
        "book_id": str(fila.get("book_id", "")),
        "book_title": str(fila.get("book_title", "Título desconocido")),
        "author": str(fila.get("author", "Autor desconocido")),
        "genres": str(fila.get("genres", "")),
        "book_details": recortar_texto(fila.get("book_details", "")),
        "average_rating": round(float(fila.get("average_rating", 0.0)), 2),

        "joy": round(float(fila.get("joy", 0.0)), 4),
        "sadness": round(float(fila.get("sadness", 0.0)), 4),
        "fear": round(float(fila.get("fear", 0.0)), 4),
        "surprise": round(float(fila.get("surprise", 0.0)), 4),
        "anger": round(float(fila.get("anger", 0.0)), 4),
        "disgust": round(float(fila.get("disgust", 0.0)), 4),
        "average_sentiment": round(float(fila.get("average_sentiment", 0.0)), 4),

        "emocion_dominante": str(fila.get("emocion_dominante", "")),
        "emocion_dominante_es": str(fila.get("emocion_dominante_es", "")),
    }


def crear_razon_recomendacion(fila):
    emotion_similarity = float(fila.get("emotion_similarity", 0.0))
    genre_similarity = float(fila.get("genre_similarity", 0.0))
    score_final = float(fila.get("score_final", 0.0))
    emocion = fila.get("emocion_dominante_es", "No disponible")
    rating = float(fila.get("average_rating", 0.0))

    return (
        f"Score final: {score_final:.2f}. "
        f"Similitud emocional: {emotion_similarity:.2f}. "
        f"Similitud de géneros: {genre_similarity:.2f}. "
        f"Emoción dominante: {emocion}. "
        f"Rating medio: {rating:.2f}."
    )


def construir_item_recomendacion(fila):
    return {
        "book_id": str(fila.get("book_id", "")),
        "book_title": str(fila.get("book_title", "Título desconocido")),
        "author": str(fila.get("author", "Autor desconocido")),
        "genres": str(fila.get("genres", "")),
        "book_details": recortar_texto(fila.get("book_details", "")),
        "average_rating": round(float(fila.get("average_rating", 0.0)), 2),

        "similarity": round(float(fila.get("similarity", 0.0)), 4),
        "score_final": round(float(fila.get("score_final", 0.0)), 4),
        "emotion_similarity": round(float(fila.get("emotion_similarity", 0.0)), 4),
        "genre_similarity": round(float(fila.get("genre_similarity", 0.0)), 4),
        "rating_score": round(float(fila.get("rating_score", 0.0)), 4),
        "same_author": bool(fila.get("same_author", False)),

        "joy": round(float(fila.get("joy", 0.0)), 4),
        "sadness": round(float(fila.get("sadness", 0.0)), 4),
        "fear": round(float(fila.get("fear", 0.0)), 4),
        "surprise": round(float(fila.get("surprise", 0.0)), 4),
        "anger": round(float(fila.get("anger", 0.0)), 4),
        "disgust": round(float(fila.get("disgust", 0.0)), 4),
        "average_sentiment": round(float(fila.get("average_sentiment", 0.0)), 4),

        "emocion_dominante": str(fila.get("emocion_dominante", "")),
        "emocion_dominante_es": str(fila.get("emocion_dominante_es", "")),
        "reason": crear_razon_recomendacion(fila),
    }

# ============================================================
# FUNCIÓN PRINCIPAL DE RECOMENDACIÓN
# ============================================================

def recomendar_por_afinidad_emocional(
    titulo_libro,
    top_n=5,
    min_reviews=1,
    excluir_mismo_autor=False,
):
    """
    Recomendación en tiempo real.

    Usa:
    - emoción calculada previamente en emotion_profiles.csv
    - géneros y rating desde books_clean.csv
    - sinopsis desde books_clean.csv
    """

    perfiles = cargar_perfiles()

    if perfiles.empty:
        return {
            "error": "No hay perfiles emocionales disponibles."
        }

    libro_base = buscar_libro_por_titulo(perfiles, titulo_libro)

    if libro_base is None:
        return {
            "error": f"No se encontró el libro: {titulo_libro}",
            "sugerencias": obtener_sugerencias_titulo(perfiles, titulo_libro),
        }

    perfiles_scored = calcular_scores(perfiles, libro_base)

    recomendaciones = perfiles_scored[
        perfiles_scored["book_id"].astype(str) != str(libro_base["book_id"])
    ].copy()

    if excluir_mismo_autor:
        autor_base = normalizar_texto(libro_base.get("author", ""))

        recomendaciones = recomendaciones[
            recomendaciones["author"].apply(normalizar_texto) != autor_base
        ].copy()

    recomendaciones = recomendaciones.sort_values(
        by=[
            "score_final",
            "genre_similarity",
            "emotion_similarity",
            "rating_score",
        ],
        ascending=[False, False, False, False],
    ).head(top_n)

    return {
        "libro_base": construir_libro_base(libro_base),
        "recomendaciones": [
            construir_item_recomendacion(fila)
            for _, fila in recomendaciones.iterrows()
        ],
    }


# ============================================================
# COMPATIBILIDAD CON MAIN ANTIGUO
# ============================================================

def find_similar_books(title, num_recommendations=5):
    resultado = recomendar_por_afinidad_emocional(
        titulo_libro=title,
        top_n=num_recommendations,
        min_reviews=1,
    )

    if "error" in resultado:
        raise ValueError(resultado["error"])

    libros_similares = []

    for rec in resultado["recomendaciones"]:
        libros_similares.append({
            "title": rec.get("book_title", "Título desconocido"),
            "author": rec.get("author", "Autor desconocido"),
            "sentiment_score": rec.get("score_final", 0.0),
            "reason": rec.get("reason", ""),
            "book_details": rec.get("book_details", ""),
        })

    return {
        "libro_original": resultado["libro_base"],
        "libros_similares": libros_similares,
    }


# ============================================================
# GENERAR RECOMENDACIONES PARA TODOS
# ============================================================

def generar_recomendaciones_para_todos(top_n=5, min_reviews=1):
    """
    Genera all_book_recommendations.csv.

    Ojo:
    - Para frontend/API no es obligatorio.
    - El endpoint /recommendations/emotional funciona en tiempo real.
    """

    perfiles = cargar_perfiles()

    if perfiles.empty:
        raise ValueError("No hay perfiles emocionales disponibles.")

    resultados = []
    total_libros = len(perfiles)

    print(f"Generando recomendaciones para {total_libros} libros...")
    print(f"Top N: {top_n}")

    perfiles = perfiles.copy().reset_index(drop=True)

    matriz_features = perfiles[EMOTION_COLUMNS].astype(float)
    matriz_similitudes = cosine_similarity(matriz_features, matriz_features)

    for idx_base, libro_base in perfiles.iterrows():
        recomendaciones = perfiles.copy()

        recomendaciones["emotion_similarity"] = matriz_similitudes[idx_base]

        generos_base = libro_base.get("genres", "")
        autor_base = normalizar_texto(libro_base.get("author", ""))

        recomendaciones["genre_similarity"] = recomendaciones["genres"].apply(
            lambda generos: calcular_jaccard_generos(generos_base, generos)
        )

        recomendaciones["rating_score"] = recomendaciones["average_rating"].apply(
            normalizar_rating
        )

        recomendaciones["same_author"] = recomendaciones["author"].apply(
            lambda autor: normalizar_texto(autor) == autor_base
        )

        recomendaciones["author_penalty"] = recomendaciones["same_author"].apply(
            lambda mismo_autor: 1.0 if mismo_autor else 0.0
        )

        recomendaciones["score_final"] = (
            recomendaciones["emotion_similarity"] * EMOTION_WEIGHT
            + recomendaciones["genre_similarity"] * GENRE_WEIGHT
            + recomendaciones["rating_score"] * RATING_WEIGHT
            - recomendaciones["author_penalty"] * AUTHOR_PENALTY_WEIGHT
        )

        recomendaciones["score_final"] = recomendaciones["score_final"].clip(
            lower=0.0,
            upper=1.0,
        )

        recomendaciones["similarity"] = recomendaciones["score_final"]

        recomendaciones = recomendaciones[
            recomendaciones["book_id"].astype(str) != str(libro_base["book_id"])
        ].copy()

        recomendaciones = recomendaciones.sort_values(
            by=[
                "score_final",
                "genre_similarity",
                "emotion_similarity",
                "rating_score",
            ],
            ascending=[False, False, False, False],
        ).head(top_n)

        libro_base_dict = construir_libro_base(libro_base)

        for posicion, (_, rec) in enumerate(recomendaciones.iterrows(), start=1):
            rec_dict = construir_item_recomendacion(rec)

            resultados.append({
                "book_id": libro_base_dict.get("book_id"),
                "book_title": libro_base_dict.get("book_title"),
                "author": libro_base_dict.get("author", ""),
                "genres": libro_base_dict.get("genres", ""),
                "book_details": libro_base_dict.get("book_details", ""),
                "average_rating": libro_base_dict.get("average_rating", 0.0),
                "emocion_dominante": libro_base_dict.get("emocion_dominante"),
                "emocion_dominante_es": libro_base_dict.get("emocion_dominante_es"),

                "recommended_rank": posicion,
                "recommended_book_id": rec_dict.get("book_id"),
                "recommended_book_title": rec_dict.get("book_title"),
                "recommended_author": rec_dict.get("author", ""),
                "recommended_genres": rec_dict.get("genres", ""),
                "recommended_book_details": rec_dict.get("book_details", ""),
                "recommended_average_rating": rec_dict.get("average_rating", 0.0),

                "score_final": rec_dict.get("score_final"),
                "similarity": rec_dict.get("similarity"),
                "emotion_similarity": rec_dict.get("emotion_similarity"),
                "genre_similarity": rec_dict.get("genre_similarity"),

                "recommended_emocion_dominante": rec_dict.get("emocion_dominante"),
                "recommended_emocion_dominante_es": rec_dict.get("emocion_dominante_es"),
                "recommended_joy": rec_dict.get("joy"),
                "recommended_sadness": rec_dict.get("sadness"),
                "recommended_fear": rec_dict.get("fear"),
                "recommended_surprise": rec_dict.get("surprise"),
                "recommended_anger": rec_dict.get("anger"),
                "recommended_disgust": rec_dict.get("disgust"),
                "recommended_average_sentiment": rec_dict.get("average_sentiment"),
                "reason": rec_dict.get("reason", ""),
            })

        contador = idx_base + 1

        if contador % 250 == 0 or contador == total_libros:
            print(f"Procesados: {contador}/{total_libros}")

    df_resultados = pd.DataFrame(resultados)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_resultados.to_csv(OUTPUT_RECOMMENDATIONS_PATH, index=False)

    print("\nArchivo creado:", OUTPUT_RECOMMENDATIONS_PATH)
    print("Total recomendaciones:", len(df_resultados))

    return df_resultados


# ============================================================
# PRUEBA LOCAL
# ============================================================

def mostrar_recomendaciones(titulo_libro, top_n=5):
    resultado = recomendar_por_afinidad_emocional(
        titulo_libro=titulo_libro,
        top_n=top_n,
    )

    if "error" in resultado:
        print("ERROR:", resultado["error"])

        if "sugerencias" in resultado:
            print("\nSugerencias:")
            for sugerencia in resultado["sugerencias"]:
                print("-", sugerencia)

        return

    libro = resultado["libro_base"]

    print("\n=== LIBRO BASE ===")
    print("Título:", libro["book_title"])
    print("Autor:", libro["author"])
    print("Géneros:", libro.get("genres", ""))
    print("Sinopsis:", libro.get("book_details", "")[:250])
    print("Rating:", libro.get("average_rating", 0.0))
    print("Emoción dominante:", libro["emocion_dominante_es"])
    print("Joy:", libro["joy"])
    print("Sadness:", libro["sadness"])
    print("Fear:", libro["fear"])
    print("Surprise:", libro["surprise"])
    print("Anger:", libro["anger"])
    print("Disgust:", libro["disgust"])
    print("Average sentiment:", libro["average_sentiment"])

    print("\n=== RECOMENDACIONES ===")

    for i, rec in enumerate(resultado["recomendaciones"], start=1):
        print(f"\n{i}. {rec['book_title']}")
        print("Autor:", rec["author"])
        print("Géneros:", rec.get("genres", ""))
        print("Sinopsis:", rec.get("book_details", "")[:250])
        print("Rating:", rec.get("average_rating", 0.0))
        print("Score final:", rec["score_final"])
        print("Similitud emocional:", rec["emotion_similarity"])
        print("Similitud géneros:", rec["genre_similarity"])
        print("Emoción dominante:", rec["emocion_dominante_es"])
        print("Reason:", rec["reason"])


if __name__ == "__main__":
    # Para no bloquearte generando todas las recomendaciones,
    # por defecto solo prueba una recomendación.
    mostrar_recomendaciones(
        titulo_libro="Harry Potter and the Half-Blood Prince",
        top_n=5,
    )

    # Si quieres generar all_book_recommendations.csv, descomenta esto:
    # generar_recomendaciones_para_todos(
    #     top_n=5,
    #     min_reviews=1,
    # )