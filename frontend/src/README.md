# 🦄 Frontend - Estructura Modular

Interfaz React para el Sistema de Recomendación de Libros.

## Estructura de carpetas

```
src/
├── components/                 # Componentes React
│   ├── RecommendationForm/    # Formulario de búsqueda
│   │   ├── RecommendationForm.jsx
│   │   ├── RecommendationForm.module.css
│   │   └── README.md
│   ├── ResultsDisplay/        # Contenedor de resultados
│   │   ├── ResultsDisplay.jsx
│   │   ├── ResultsDisplay.module.css
│   │   └── README.md
│   ├── BookCard/              # Tarjeta individual de libro
│   │   ├── BookCard.jsx
│   │   ├── BookCard.module.css
│   │   └── README.md
│   └── LoadingSpinner/        # Indicador de carga
│       ├── LoadingSpinner.jsx
│       ├── LoadingSpinner.module.css
│       └── README.md
├── styles/                    # Estilos globales
│   ├── variables.css          # Variables de tema (colores, tipografía, spacing)
│   └── global.css             # Reset y estilos base
├── App.jsx                    # Componente raíz
├── App.module.css             # Estilos de App
├── index.jsx                  # Punto de entrada
└── index.css                  # Estilos del DOM (importa global.css)
```

## Filosofía de diseño

### 🎨 Tema Editorial
- **Colores**: Paleta cálida inspirada en libros antiguos (marrón, beige, dorado)
- **Tipografía**: Georgia/Garamond para headings, sans-serif para body
- **Espaciado**: Generoso y respirable, como un libro bien editado

### 📱 Responsivo
- **Mobile-first**: Diseño comienza en mobile y escala hacia arriba
- **Breakpoints principales**:
  - `< 640px` - Mobile
  - `640-768px` - Tablet pequeña
  - `768-1024px` - Tablet grande
  - `> 1024px` - Desktop

### 🎯 BEM (Block Element Modifier)
Todos los estilos siguen metodología BEM:
```css
.block { }
.block__element { }
.block__element--modifier { }
```

Ejemplo:
```css
.form { }                     /* Block */
.form__input { }              /* Element */
.form__button--loading { }    /* Modifier */
```

## Componentes

### RecommendationForm
**Props**: `onSubmit`, `disabled`

Captura la búsqueda del usuario (título + descripción del libro).

### ResultsDisplay
**Props**: `recommendations`, `originalBook`

Muestra las 5 recomendaciones usando componentes BookCard.

### BookCard
**Props**: `book`, `position`

Tarjeta individual con:
- Ranking visual (1-5)
- Barra de similitud emocional
- Título, autor, razón

### LoadingSpinner
**Props**: ninguno

Indicador de carga mientras el backend procesa.

## CSS Modules

**¿Por qué usamos CSS Modules?**

```jsx
// ✅ Bueno - Scoped, no hay conflictos de nombres
import styles from './Component.module.css';
<div className={styles.component__element} />

// ❌ Malo - Global, riesgo de conflictos
import './Component.css';
<div className="component__element" />
```

**Cómo usarlos:**

```jsx
import styles from './RecommendationForm.module.css';

<form className={styles.form}>
  <input className={styles.form__input} />
  <button className={styles.form__button}>
</form>
```

## Variables CSS

Todas las variables están en `styles/variables.css`:

```css
:root {
  --color-primary: #8B6F47;              /* Marrón */
  --color-accent: #D4AF37;               /* Dorado */
  --font-size-h2: 2rem;
  --spacing-lg: 1.5rem;
  --border-radius-md: 8px;
  /* ... más variables */
}
```

**Beneficios:**
- Tema consistente en toda la app
- Fácil de cambiar (busca/reemplaza)
- Responsive (variables cambian por breakpoint)

## Flujo de datos

```
App (estado, API calls)
  ↓
  ├─ RecommendationForm (entrada)
  │   └─ onSubmit → API call
  ├─ LoadingSpinner (while loading)
  └─ ResultsDisplay (salida)
      └─ BookCard × 5 (cada recomendación)
```

**No hay prop drilling innecesario:**
- Los componentes solo reciben lo que necesitan
- Los callbacks suben solo un nivel

## Mejoras para estudiantes

### Easy
- [ ] Cambiar colores en `variables.css`
- [ ] Agregar más emojis o iconos
- [ ] Cambiar fuentes

### Medium
- [ ] Agregar página de "Acerca de"
- [ ] Historial de búsquedas
- [ ] Favoritos

### Hard
- [ ] Gráficos de emociones (chart.js)
- [ ] Filtros avanzados
- [ ] Tema claro/oscuro

## Debugging

### DevTools React
```bash
# En Chrome:
1. Instala React Developer Tools
2. F12 → Components tab
3. Inspecciona componentes, props, estado
```

### Console
```javascript
// Desde el componente:
console.log('Props:', props);
console.log('Estado:', state);
```

### Network
```
F12 → Network → XHR
Inspecciona llamadas a /recommend
```

## Performance

- ✅ **CSS Modules**: Sin CSS innecesario
- ✅ **Componentes pequeños**: Fáciles de optimizar
- ✅ **Sin re-renders innecesarios**: Props bien definidas

## Accesibilidad

- ✅ Labels conectados a inputs (`htmlFor`)
- ✅ Aria attributes en elementos interactivos
- ✅ Contraste de colores adecuado
- ✅ Navegación por keyboard

## Notas para estudiantes

1. **Lee los READMEs** de cada componente
2. **Sigue BEM** en cualquier CSS nuevo
3. **Usa variables CSS** en lugar de hardcodear colores
4. **Mobile-first**: Diseña para mobile, escala a desktop
5. **Modular**: Cada componente en su carpeta
6. **Documenta**: Agrega comentarios si cambias lógica

---

Del unicornio que se piró. Adelante. 🦄
