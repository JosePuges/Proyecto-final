"""
🦄 Cache Manager - Persistencia de resultados

Responsable de:
1. Guardar análisis (para no repetir BERT cada vez)
2. Cargar análisis del caché
3. Validar que el caché es válido
4. Limpiar caché si es necesario

Por qué es crítico:
- BERT tarda 1-2 segundos por review
- 200 reviews = 3-6 minutos
- Sin caché: CADA consulta tarda 6 minutos ❌
- Con caché: Primera consulta 6 min, resto <100ms ✅
"""

import json
import os
import pickle
from datetime import datetime
from typing import Optional, Dict
import hashlib

# ============================================
# CONFIGURACIÓN
# ============================================

CACHE_DIR = os.path.join(os.path.dirname(__file__), '../../cache')
SENTIMENT_CACHE_FILE = os.path.join(CACHE_DIR, 'sentiment_profiles.json')
EMOTION_PROFILES_CACHE = os.path.join(CACHE_DIR, 'emotion_profiles.pkl')

# Crear directorio si no existe
os.makedirs(CACHE_DIR, exist_ok=True)

# ============================================
# CACHÉ MANAGER
# ============================================

class CacheManager:
    """
    Gestiona persistencia de análisis en disco.

    Usa JSON para sentimientos (legible) y pickle para perfiles grandes (rápido).
    """

    def __init__(self, cache_dir: str = CACHE_DIR):
        """
        Inicializa el manager.

        Args:
            cache_dir: Directorio donde guardar caché
        """
        self.cache_dir = cache_dir
        self.sentiment_file = os.path.join(cache_dir, 'sentiment_profiles.json')
        self.emotion_profiles_file = os.path.join(cache_dir, 'emotion_profiles.pkl')
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Crea directorio si no existe."""
        os.makedirs(self.cache_dir, exist_ok=True)

    # ========================
    # SENTIMENT PROFILES (JSON)
    # ========================

    def get_sentiment_profile(self, book_title: str) -> Optional[Dict]:
        """
        Obtiene perfil emocional del caché.

        Args:
            book_title: Título del libro

        Returns:
            Dict con emociones, o None si no existe

        Ejemplo:
            cache = CacheManager()
            profile = cache.get_sentiment_profile("The Midnight Library")
            # Retorna: {"joy": 0.75, "sadness": 0.2, ...}
        """
        try:
            with open(self.sentiment_file, 'r') as f:
                profiles = json.load(f)
                return profiles.get(book_title)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print("⚠️ Caché corrupto, reconstruyendo...")
            return None

    def save_sentiment_profile(self, book_title: str, profile: Dict):
        """
        Guarda perfil emocional en caché.

        Args:
            book_title: Título del libro
            profile: Dict con 6 emociones

        Ejemplo:
            cache = CacheManager()
            profile = {"joy": 0.75, "sadness": 0.2, ...}
            cache.save_sentiment_profile("The Midnight Library", profile)
        """
        # Cargar caché existente
        profiles = {}
        if os.path.exists(self.sentiment_file):
            try:
                with open(self.sentiment_file, 'r') as f:
                    profiles = json.load(f)
            except json.JSONDecodeError:
                profiles = {}

        # Agregar nuevo perfil
        profiles[book_title] = {
            **profile,
            "_timestamp": datetime.now().isoformat()
        }

        # Guardar
        with open(self.sentiment_file, 'w') as f:
            json.dump(profiles, f, indent=2)

    def clear_sentiment_cache(self):
        """Limpia todo el caché de sentimientos."""
        if os.path.exists(self.sentiment_file):
            os.remove(self.sentiment_file)
            print("✓ Caché de sentimientos limpiado")

    # ========================
    # EMOTION PROFILES (PICKLE)
    # ========================

    def save_emotion_profiles(self, profiles_df):
        """
        Guarda dataframe de perfiles emocionales en pickle (rápido para lectura).

        Args:
            profiles_df: DataFrame con perfiles de todos los libros

        Nota:
            Usa pickle porque es más rápido que CSV para DataFrames grandes.
            Algo como 60K libros × 6 emociones = necesitamos velocidad.

        Ejemplo:
            cache = CacheManager()
            cache.save_emotion_profiles(all_emotion_profiles_df)
        """
        with open(self.emotion_profiles_file, 'wb') as f:
            pickle.dump(profiles_df, f)
        print(f"✓ Guardado: {profiles_df.shape[0]} perfiles emocionales")

    def load_emotion_profiles(self):
        """
        Carga dataframe de perfiles emocionales.

        Returns:
            DataFrame o None si no existe

        Ejemplo:
            cache = CacheManager()
            profiles = cache.load_emotion_profiles()
        """
        if not os.path.exists(self.emotion_profiles_file):
            return None

        try:
            with open(self.emotion_profiles_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando caché: {e}")
            return None

    # ========================
    # ESTADÍSTICAS
    # ========================

    def get_cache_stats(self) -> Dict:
        """
        Obtiene estadísticas del caché actual.

        Returns:
            Dict con información del caché
        """
        stats = {
            "cached_books": 0,
            "total_size_mb": 0,
            "last_updated": None
        }

        # Contar sentimientos cacheados
        if os.path.exists(self.sentiment_file):
            try:
                with open(self.sentiment_file, 'r') as f:
                    profiles = json.load(f)
                    stats["cached_books"] = len(profiles)
                    stats["last_updated"] = profiles.get("_timestamp")
            except:
                pass

        # Tamaño total
        for filename in [self.sentiment_file, self.emotion_profiles_file]:
            if os.path.exists(filename):
                size = os.path.getsize(filename) / (1024 * 1024)  # MB
                stats["total_size_mb"] += size

        return stats

    def clear_all(self):
        """Limpia TODO el caché."""
        for f in [self.sentiment_file, self.emotion_profiles_file]:
            if os.path.exists(f):
                os.remove(f)
        print("✓ Todo el caché limpiado")


# ============================================
# FUNCIONES HELPER (Decorator pattern)
# ============================================

def cache_sentiment(func):
    """
    Decorator para cachear automáticamente análisis de sentimientos.

    Uso:
        @cache_sentiment
        def analyze_sentiment(book_title):
            # Código lento aquí
            pass

    Comportamiento:
        1. Busca en caché
        2. Si existe: retorna
        3. Si no existe: ejecuta función, guarda y retorna
    """
    cache = CacheManager()

    def wrapper(book_title: str):
        # Intentar obtener del caché
        cached = cache.get_sentiment_profile(book_title)
        if cached:
            print(f"📦 Usando caché para '{book_title}'")
            return cached

        # Ejecutar función (lento)
        print(f"⏳ Analizando '{book_title}' (sin caché)...")
        result = func(book_title)

        # Guardar en caché
        if result is not None:
            cache.save_sentiment_profile(book_title, result)
        else:
            print(f"  ⚠️ Sin reviews para '{book_title}', no se cachea")

        return result

    return wrapper


# ============================================
# DEBUGGING / TESTING
# ============================================

if __name__ == "__main__":
    cache = CacheManager()

    # Guardar un perfil
    profile = {
        "joy": 0.75,
        "sadness": 0.2,
        "fear": 0.1,
        "surprise": 0.65,
        "anger": 0.05,
        "disgust": 0.08,
    }

    print("Guardando perfil...")
    cache.save_sentiment_profile("The Midnight Library", profile)

    print("\nCargando perfil...")
    loaded = cache.get_sentiment_profile("The Midnight Library")
    print(f"Cargado: {loaded}")

    print("\nEstadísticas:")
    stats = cache.get_cache_stats()
    print(f"Libros en caché: {stats['cached_books']}")
    print(f"Tamaño: {stats['total_size_mb']:.2f} MB") 
    