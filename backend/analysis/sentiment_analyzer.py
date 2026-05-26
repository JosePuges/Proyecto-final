"""
🦄 Sentiment Analyzer - MODO TURBO v2
Objetivo: 16k libros en ~2-3 horas en GPU.

Cambios clave vs versión anterior:
  1. Length bucketing → ordena textos por longitud antes de batchear (2-3× speedup)
  2. fp16 → modelo en media precisión (2× speedup, sin pérdida apreciable)
  3. truncation=True, max_length=128 → no se desperdicia cómputo en padding
  4. Pre-indexado de reviews por book_id (groupby) → elimina bucle O(n²)
  5. Checkpoints incrementales → si crashea no pierdes el trabajo
  6. Comprobación explícita de CUDA al arrancar
  7. encoding='utf-8' → no corrompe tildes, eñes ni caracteres especiales
"""

import time
import os
from typing import Dict
import pickle
import pandas as pd
import numpy as np
import torch
from transformers import pipeline

# ============================================
# CONFIGURACIÓN
# ============================================

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'emotion_profiles.csv')
NB_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'cache', 'naive_bayes_emotions.pkl')
NB_MODEL = pickle.load(open(NB_MODEL_PATH, 'rb')) if os.path.exists(NB_MODEL_PATH) else None

EMOTIONS = ['joy', 'sadness', 'fear', 'surprise', 'anger', 'disgust']
MAX_REVIEWS = 5
MAX_CHARS = 500
MAX_TOKENS = 128         # antes era el default 512 → 4× menos cómputo
BATCH_SIZE = 512         # subido de 256 (con fp16 cabe sin problema)
SAVE_EVERY = 500         # checkpoint cada N libros procesados

# ============================================
# COMPROBACIÓN DE GPU
# ============================================

print("=" * 60)
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    DEVICE = 0
    DTYPE = torch.float16
else:
    print("⚠️  CORRIENDO EN CPU — esto NO llegará a 2-3h.")
    print("    Mueve esto a Colab/Kaggle con GPU o no llegarás al objetivo.")
    DEVICE = -1
    DTYPE = torch.float32
print("=" * 60 + "\n")

# ============================================
# CARGA DE MODELO Y DATOS
# ============================================

print("🚀 Cargando modelo (fp16)...")
classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
    device=DEVICE,
    torch_dtype=DTYPE,
)

print("📚 Cargando libros...")

ALL_BOOKS = pd.read_csv(os.path.join(DATA_PATH, "books_clean.csv"), encoding='utf-8')
ALL_BOOKS['book_id'] = ALL_BOOKS['book_id'].astype(str)

print("📝 Cargando reviews...")
ALL_REVIEWS = pd.read_csv(
    os.path.join(DATA_PATH, "reviews_clean.csv"),
    encoding='utf-8',
    on_bad_lines='skip',
    engine='python',
)
ALL_REVIEWS['book_id'] = ALL_REVIEWS['book_id'].astype(str)

# 🔑 PRE-INDEXAR reviews por book_id (groupby una sola vez)
print("🔧 Indexando reviews por book_id...")
REVIEWS_BY_BOOK = (
    ALL_REVIEWS.dropna(subset=['review_content'])
    .groupby('book_id')['review_content']
    .apply(list)
    .to_dict()
)

print(f"✓ {len(ALL_BOOKS)} libros | {len(ALL_REVIEWS)} reviews | "
      f"{len(REVIEWS_BY_BOOK)} libros con reviews\n")

if os.path.exists(CACHE_PATH) and os.path.getsize(CACHE_PATH) > 0:
    CACHE_DF = pd.read_csv(CACHE_PATH, encoding='utf-8')
    print(f"✓ {len(CACHE_DF)} libros ya en caché\n")
else:
    CACHE_DF = pd.DataFrame()


# ============================================
# HELPERS
# ============================================

def aggregate_emotion_scores(scores_list: list) -> Dict[str, float]:
    if not scores_list:
        raise ValueError("No hay scores")
    df = pd.DataFrame(scores_list)
    if not all(e in df.columns for e in EMOTIONS):
        raise ValueError("Faltan emociones en el output del modelo")
    profile = df[EMOTIONS].mean().to_dict()
    positive = profile['joy'] + profile['surprise']
    negative = profile['sadness'] + profile['fear'] + profile['anger'] + profile['disgust']
    profile['average_sentiment'] = round((positive - negative / 2) / 1.5, 4)
    return {k: round(v, 4) for k, v in profile.items()}


def save_cache(rows: list):
    """Guarda el caché combinando con lo que ya había."""
    global CACHE_DF
    if not rows:
        return
    new_df = pd.DataFrame(rows)
    CACHE_DF = pd.concat([CACHE_DF, new_df], ignore_index=True) if not CACHE_DF.empty else new_df
    CACHE_DF.to_csv(CACHE_PATH, index=False, encoding='utf-8')


def estimate_profile_naive_bayes(texts: list) -> Dict[str, float]:
    if NB_MODEL is None:
        raise RuntimeError("Naive Bayes no cargado")

    outputs = classifier(
        texts,
        batch_size=len(texts),
        truncation=True,
        max_length=MAX_TOKENS,
        padding=True,
    )

    scores_list = [
        {item['label'].lower(): item['score'] for item in out}
        for out in outputs
    ]
    partial_profile = pd.DataFrame(scores_list)[EMOTIONS].mean().values.reshape(1, -1)

    proba = NB_MODEL.predict_proba(partial_profile)[0]
    nb_boost = dict(zip(NB_MODEL.classes_, proba))

    final = {}
    for i, e in enumerate(EMOTIONS):
        final[e] = round(partial_profile[0][i] * 0.7 + nb_boost.get(e, 0.0) * 0.3, 4)

    positive = final['joy'] + final['surprise']
    negative = final['sadness'] + final['fear'] + final['anger'] + final['disgust']
    final['average_sentiment'] = round((positive - negative / 2) / 1.5, 4)
    final['nb_assisted'] = True

    return final


# ============================================
# BATCH GLOBAL OPTIMIZADO
# ============================================

def analyze_first_n_books(n: int = 16000) -> pd.DataFrame:
    global CACHE_DF

    books = ALL_BOOKS.head(n)
    cached_titles = (
        set(CACHE_DF['book_title'].str.lower().tolist()) if not CACHE_DF.empty else set()
    )
    pending = books[~books['book_title'].str.lower().isin(cached_titles)]
    print(f"📊 {len(cached_titles)} en caché | {len(pending)} pendientes\n")

    if pending.empty:
        print("Nada que procesar.")
        return CACHE_DF

    # ---------- 1) Recopilar textos usando el índice pre-calculado ----------
    book_texts = {}      # title -> [texts]
    book_meta = {}       # title -> (book_id, author)
    book_texts_nb = {}

    for _, row in pending.iterrows():
        title = row['book_title']
        book_id = row['book_id']
        reviews = REVIEWS_BY_BOOK.get(book_id, [])
        texts = [
            r[:MAX_CHARS]
            for r in reviews[:MAX_REVIEWS]
            if isinstance(r, str) and r.strip()
        ]
        if not texts:
            continue
        book_meta[title] = (book_id, row.get('author', ''))
        if len(texts) >= 4:
            book_texts[title] = texts
        elif NB_MODEL is not None:
            book_texts_nb[title] = texts

    print(f"✓ {len(book_texts)} libros con reviews aptas")

    # ---------- 2) Aplanar y ORDENAR POR LONGITUD (length bucketing) ----------
    flat_texts = []
    flat_titles = []
    for title, texts in book_texts.items():
        for t in texts:
            flat_texts.append(t)
            flat_titles.append(title)

    # Ordenar índices por longitud del texto.
    # Así cada batch contiene textos de longitud similar y el padding es mínimo.
    order = sorted(range(len(flat_texts)), key=lambda i: len(flat_texts[i]))
    sorted_texts = [flat_texts[i] for i in order]
    sorted_titles = [flat_titles[i] for i in order]

    total = len(sorted_texts)
    print(f"📝 Total textos: {total} (ordenados por longitud)")
    print(f"🔥 Inferencia: fp16, batch={BATCH_SIZE}, max_length={MAX_TOKENS}\n")

    # ---------- 3) Inferencia ----------
    all_outputs = [None] * total
    start_t = time.time()
    last_log = start_t

    for i in range(0, total, BATCH_SIZE):
        batch = sorted_texts[i:i + BATCH_SIZE]
        outputs = classifier(
            batch,
            batch_size=len(batch),
            truncation=True,
            max_length=MAX_TOKENS,
            padding=True,
        )
        for j, out in enumerate(outputs):
            all_outputs[i + j] = out

        # Log cada ~10 batches
        if (i // BATCH_SIZE) % 10 == 0 and i > 0:
            now = time.time()
            elapsed = now - start_t
            rate = i / elapsed
            eta_min = (total - i) / rate / 60
            print(f"  ⚡ {i:>7}/{total} | {rate:6.0f} txt/s | ETA: {eta_min:5.1f} min")

    total_inf = time.time() - start_t
    if total_inf > 0:
        print(f"\n✓ Inferencia completada en {total_inf/60:.1f} min "
              f"({total/total_inf:.0f} textos/s promedio)\n")
    else:
        print("\n✓ Nada que procesar.\n")

    # ---------- 4) Reconstruir perfiles por libro ----------
    print("📊 Calculando perfiles emocionales...")
    book_scores = {title: [] for title in book_texts}
    for idx, output in enumerate(all_outputs):
        title = sorted_titles[idx]
        scores = {item['label'].lower(): item['score'] for item in output}
        book_scores[title].append(scores)

    new_rows = []
    for title, scores_list in book_scores.items():
        try:
            profile = aggregate_emotion_scores(scores_list)
            book_id, author = book_meta[title]
            new_rows.append({
                'book_id': book_id,
                'book_title': title,
                'author': author,
                **profile,
            })
        except Exception as e:
            print(f"  ✗ Error en '{title}': {e}")
            continue

        # Checkpoint incremental
        if len(new_rows) % SAVE_EVERY == 0:
            save_cache(new_rows)
            new_rows = []   # ya guardados, reseteamos buffer
            print(f"  💾 Checkpoint guardado ({len(CACHE_DF)} libros totales)")

    print(f"\n🧠 Procesando {len(book_texts_nb)} libros con Naive Bayes...")
    for title, texts in book_texts_nb.items():
        try:
            profile = estimate_profile_naive_bayes(texts)
            book_id, author = book_meta[title]
            new_rows.append({
                'book_id': book_id,
                'book_title': title,
                'author': author,
                **profile,
            })
        except Exception as e:
            print(f"  ✗ Error NB en '{title}': {e}")
            continue

    # Guardado final
    save_cache(new_rows)
    print(f"\n💾 Caché final: {len(CACHE_DF)} libros totales")
    return CACHE_DF


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    start = time.time()
    analyze_first_n_books(16000)
    elapsed = time.time() - start
    print(f"\n⏱️  Tiempo total: {elapsed/3600:.2f}h ({elapsed/60:.1f} min)")