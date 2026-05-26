# 📊 ResultsDisplay

Componente que muestra las recomendaciones obtenidas del backend.

## Estructura

```
ResultsDisplay/
├── ResultsDisplay.jsx          # Lógica del componente
├── ResultsDisplay.module.css   # Estilos con BEM
└── README.md                   # Este archivo
```

## Props

| Prop | Tipo | Descripción |
|------|------|-------------|
| `recommendations` | `object` | Respuesta del API con recomendaciones |
| `originalBook` | `string` | Título del libro que el usuario buscó |

## Estructura esperada de `recommendations`

```javascript
{
  original_book: "The Midnight Library",
  recommendations: [
    {
      title: "Piranesi",
      author: "Susanna Clarke",
      sentiment_score: 0.78,
      reason: "Similar emotional impact"
    },
    // ... hasta 5 recomendaciones
  ],
  analysis_summary: "Resumen del análisis emocional realizado"
}
```

## Ejemplo de uso

```jsx
import ResultsDisplay from './components/ResultsDisplay/ResultsDisplay';

const recommendations = {
  original_book: "The Midnight Library",
  recommendations: [/* ... */],
  analysis_summary: "Análisis de 200 reseñas..."
};

<ResultsDisplay 
  recommendations={recommendations}
  originalBook="The Midnight Library"
/>
```

## Características

- 🎯 **Grid responsivo** - Se adapta a mobile, tablet, desktop
- 📚 **Integración con BookCard** - Reutiliza componente para cada recomendación
- ✨ **Animación de entrada** - Fade-in elegante
- 📱 **Mobile-first** - Diseño fluido en todos los dispositivos

## CSS Classes (BEM)

### Block: `.results`
- `.results` - Contenedor principal

### Elements:
- `.results__header` - Encabezado con título
- `.results__title` - H2 principal
- `.results__book` - El nombre del libro buscado
- `.results__summary` - Resumen del análisis
- `.results__grid` - Contenedor grid de BookCard
- `.results__footer` - Información adicional al pie
- `.results__footer__text` - Texto del footer

## Responsividad

- **Desktop** (> 1024px): Grid de 3 columnas
- **Tablet** (768-1024px): Grid de 2 columnas
- **Mobile** (< 768px): Grid de 1 columna (stack)

## Guardias

- ✅ Si `recommendations` es null/undefined, no renderiza nada
- ✅ Si `recommendations.recommendations` no existe, no renderiza nada
- ✅ Solo renderiza si hay datos válidos

## Mejoras posibles

- [ ] Paginación si hay más de 5 recomendaciones
- [ ] Botón "Obtener más recomendaciones"
- [ ] Filtros por sentimiento (mostrar solo alegres, tristes, etc.)
- [ ] Comparador visual de perfiles emocionales
- [ ] Exportar resultados a PDF/imagen

## Notas para estudiantes

Este componente es el "contenedor" de recomendaciones.
- Recibe datos del padre (App.jsx)
- Usa BookCard para renderizar cada libro
- Es principalmente presentacional

Si quieres agregar interactividad:
1. Agrega estado en el componente padre (App.jsx)
2. Pasa callbacks a este componente
3. O a sus hijos (BookCard)
