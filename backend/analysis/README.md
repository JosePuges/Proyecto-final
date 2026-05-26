# 🦄 Backend Analysis - El marrón técnico

Aquí está TODO lo que me dejé sin terminar. Los módulos Python que ustedes van a tener que acabar.

## La estructura

```
analysis/
├── __init__.py                  
├── sentiment_analyzer.py        # ← USTEDES AQUÍ: BERT analysis
├── recommender.py               # ← USTEDES AQUÍ: similitud emocional
├── data_processor.py            # Ya empezado: cargar datos limpios
├── cache_manager.py             # ✓ YA HECHO (menos mal, ahorren una semana)
└── README.md                    # Este archivo
```

## Cómo funciona

```
Usuario: "Busco algo como The Midnight Library"
    ↓
main.py → POST /recommend
    ↓
sentiment_analyzer.analyze_sentiment()
├─ Buscar las reviews de ese libro
├─ BERT → detecta 6 emociones en cada review (LENTO, 1-2 seg por review)
└─ Promedia todo en un perfil: {joy: 0.75, sadness: 0.2, ...}
    ↓
cache_manager → "Guardo esto para no repetir en 6 minutos"
    ↓
recommender.find_similar_books()
├─ Cargo todos los perfiles emocionales (de todos los 16K libros)
├─ Calculo similitud coseno (qué tan parecido es el perfil)
└─ Retorno TOP 5
    ↓
Frontend muestra las 5 recomendaciones bonitas
```

## Lo que tengo para ustedes

### ✅ YA HECHO (no me lo toquen)

**cache_manager.py** - Sistema de caché
- Guarda análisis para no repetir BERT cada vez
- Carga rápido (<100ms)
- Sin esto, cada búsqueda tarda 6 minutos
- CRÍTICO para que no sufran

**data_processor.py** - Cargador de datos
- Templates para `load_dataset()`, `preprocess_reviews()`, `clean_text()`
- Ustedes completan la lógica
- Aquí es donde limpian la data dirty

### ⚠️ TODO: USTEDES COMPLETAN

**sentiment_analyzer.py** - Análisis de emociones
```python
def analyze_sentiment(book_title: str) -> dict:
    # 1. Cargar reviews del libro
    # 2. BERT inference → 6 emociones (joy, sadness, fear, surprise, anger, disgust)
    # 3. Agregar en perfil único
    # 4. Retornar dict con los 6 scores
```

**Realidad**: BERT es lentísimo. Una búsqueda sin caché = 3-6 minutos. Con caché = <100ms. Hagan bien el caché o sufrirán.

**recommender.py** - Motor de recomendación
```python
def find_similar_books(sentiment_profile: dict, num_recommendations: int = 5) -> list:
    # 1. Cargar perfiles pre-calculados de todos los libros
    # 2. Cosine similarity entre el perfil input y todos
    # 3. Retornar TOP 5 ordenados por similitud
```

**Realidad**: Si no pre-calculan los perfiles de todos los libros, esto será más lento que BERT. El caché es vuestro amigo.

## Timeline (No es broma)

**Semana 1: Exploración**
- Cargar datos
- Ver qué hay (EDA básico)
- Limpiar reviews sucias (hay mucho spam)

**Semana 2: BERT (el valle de la muerte)**
- Cargar modelo BERT
- Hacer inference en 10 reviews (testing)
- Resultado: "¿Por qué tarda 20 segundos en 10 reviews?"
- Alguien va a querer tirar la computadora
- No renuncien

**Semana 3: Similitud + TOP 5**
- Pre-calcular perfiles de los 16K libros
- Implementar cosine similarity
- Verificar que los TOP 5 tienen sentido
- Cachear todo

**Semana 4: Pulir**
- Testing
- Optimizaciones (batching, quantization)
- Demo en vivo

## Advertencias del Unicornio

### ⚠️ BERT es LENTÍSIMO

Realidad:
- 1 review = 1-2 segundos
- 200 reviews = 3-6 MINUTOS
- 16K libros = semanas (no hagas esto)

Solución:
- Pre-calcula los TOP 100-1000 libros UNA SOLA VEZ
- Guarda en caché con `cache_manager`
- Próximas búsquedas: <100ms

Ni se os ocurra hacer inference on-demand de todos los libros.

### ⚠️ Data dirty

Las 63K reviews tienen:

- Emojis raros 🤪🎪👻
- Idiomas mezclados (inglés + español + alemán)
- Bots escribiendo "5 stars" 100 veces
- Reviews de 1 carácter ("")
- Caracteres especiales y encoding roto

Resultado: Si no limpian bien, BERT falla o te retorna basura.

Solución: `preprocess_reviews()` + `clean_text()`

### ⚠️ Cosine similarity puede engañar

Si dos perfiles son muy parecidos, la similitud te dará 0.9.
Pero puede ser que ambos sean "tristes" cuando uno es "alegre".

Verificad manualmente si los TOP 5 tienen sentido.

## Empezar

**Paso 1: Ver qué hay**
```python
cd backend
python analysis/data_processor.py
# Deberías ver info del dataset
```

**Paso 2: Levantar la API**
```python
# Terminal 1
python -m uvicorn main:app --reload

# Terminal 2: Probar
curl http://localhost:8000/health
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"title": "The Midnight Library"}'
# Retorna placeholder (ustedes lo implementan)
```

**Paso 3: Empezar con sentiment_analyzer.py**
```python
# Testing local
python analysis/sentiment_analyzer.py
```

## Debugging cuando todo se rompe

```python
# En sentiment_analyzer.py
print(f"[BÚSQUEDA] Libro: {book_title}")
print(f"[DATOS] Reviews encontradas: {len(reviews)}")
print(f"[BERT] Procesando {len(reviews)} reviews...")
print(f"[RESULTADO] Perfil: {sentiment_profile}")

# En recommender.py
print(f"[CACHÉ] Perfiles cargados: {all_profiles.shape}")
print(f"[SIMILITUD] Top 10 scores: {similarities[:10]}")
print(f"[RESULTADO] Retornando: {recommendations}")
```

## Checklist: "¿Esto está hecho?"

- [ ] `load_dataset()` carga libros y reviews sin errores
- [ ] `preprocess_reviews()` limpia 63K → ~60K reviews
- [ ] `analyze_sentiment()` retorna un dict con 6 emociones
- [ ] BERT funciona en 10 reviews (no perfecto, pero funciona)
- [ ] Cache guarda/carga sin problemas
- [ ] `find_similar_books()` retorna TOP 5 con sense
- [ ] POST /recommend tarda <1 segundo (con caché)
- [ ] Frontend puede llamar y obtener recomendaciones
- [ ] Demo en vivo funciona (probablemente no, pero lo intenten)

## Lo que pueden mejorar (Semana 4+)

- [ ] Búsqueda fuzzy (si escriben "Midnight Libary" igual funciona)
- [ ] Fallback a autor si no encuentran por título
- [ ] K-means clustering (agrupar libros por "tipo")
- [ ] Quantization de BERT (hace inference más rápido)
- [ ] API docs (Swagger, ya funciona en /docs)
- [ ] Tests (pytest)

## Últimas palabras

Python, no JavaScript. La lógica está en `analysis/`.
El caché es vuestro mejor amigo.
BERT es lento, pero funciona.
Los datos son dirty, limpienlos.

Si esto funciona el 28, van a causar impresión.
Si no funciona, al menos aprenderán cómo NO hacerlo.

No me defraudan.

---

Del Unicornio que se piró. Adelante. 🦄
