# 📖 BookCard

Componente reutilizable para mostrar una recomendación individual.

## Estructura

```
BookCard/
├── BookCard.jsx          # Lógica del componente
├── BookCard.module.css   # Estilos con BEM
└── README.md             # Este archivo
```

## Props

| Prop | Tipo | Descripción |
|------|------|-------------|
| `book` | `object` | Objeto con estructura: `{ title, author, sentiment_score, reason }` |
| `position` | `number` | Número de posición en ranking (1-5) |

## Estructura esperada de `book`

```javascript
{
  title: "Piranesi",
  author: "Susanna Clarke",
  sentiment_score: 0.78,
  reason: "Similar emotional impact and introspective narrative"
}
```

## Ejemplo de uso

```jsx
import BookCard from './components/BookCard/BookCard';

const book = {
  title: "The Night Circus",
  author: "Erin Morgenstern",
  sentiment_score: 0.82,
  reason: "Comparte la atmósfera mágica y reflexiva"
};

<BookCard book={book} position={1} />
```

## Características

- ✨ **Ranking visual** - Número de posición en círculo degradado
- 📊 **Barra de sentimiento** - Muestra % de similitud emocional
- 🎨 **Colores adaptativos** - El color de la barra cambia según el score:
  - Verde (80%+) - Muy similar
  - Dorado (65-79%) - Bastante similar
  - Ámbar (50-64%) - Similar
  - Cobre (<50%) - Algo similar
- 🏷️ **Accesibilidad** - Incluye atributos ARIA para screen readers

## CSS Classes (BEM)

### Block: `.card`
- `.card` - Contenedor principal

### Elements:
- `.card__rank` - Círculo con número de posición
- `.card__rank__number` - El número dentro
- `.card__content` - Contenedor de contenido
- `.card__header` - Título y autor
- `.card__title` - H3 del libro
- `.card__author` - Nombre del autor
- `.card__sentiment` - Contenedor de barra
- `.card__sentiment__bar` - Fondo de la barra
- `.card__sentiment__fill` - Relleno animado
- `.card__sentiment__label` - Porcentaje
- `.card__reason` - Párrafo de razón
- `.card__reason__icon` - Emoji inicial

## Responsividad

- **Desktop** (> 768px): Diseño horizontal con rank a la izquierda
- **Tablet** (640-768px): Padding reducido, font ajustados
- **Mobile** (< 640px): Diseño vertical (rank arriba), todo más compacto

## Animaciones

- Hover: Sube 4px y aumenta sombra
- Barra de sentimiento: Relleno anima suavemente

## Mejoras posibles

- [ ] Click en tarjeta → Mostrar más detalles
- [ ] Botón "Agregar a wishlist"
- [ ] Enlace a Goodreads
- [ ] Mostrar perfiles emocionales (6 emociones)
- [ ] Botón para obtener más recomendaciones basadas en este libro

## Notas para estudiantes

Este es un componente **presentacional** - solo recibe props y renderiza.
La lógica de datos está en el padre (`ResultsDisplay`).

Si quieres agregar interactividad:
1. Agrega un `onClick` a `.card`
2. Pasa una función callback desde el padre
3. Maneja el estado en el componente padre
