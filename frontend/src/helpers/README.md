# Helpers - Utilidades de la Aplicación

Funciones y constantes reutilizables en la app.

## colorPalette.js

**Paleta de colores cálida y vibrante** (estilo portalápices: naranja → magenta → verde mint sobre fondo claro).

### Uso en componentes

```javascript
import { colorPalette, gradients, shadows } from '@/helpers/colorPalette';

// En CSS-in-JS o styled-components
const headerStyle = {
  background: gradients.header,
  color: colorPalette.textPrimary,
  boxShadow: shadows.lg,
};

// O pasar a CSS modules
<div style={{ color: colorPalette.accent }}>Texto magenta</div>
```

### Colores disponibles

```javascript
colorPalette.primary       // #0099FF (Azul vibrante)
colorPalette.accent        // #FF1493 (Magenta)
colorPalette.success       // #00FF7F (Verde neón)
colorPalette.warning       // #FF6B35 (Naranja)
colorPalette.error         // #FF3333 (Rojo)
colorPalette.textPrimary   // #FFFFFF (Blanco)
colorPalette.bgPrimary     // #0A0E27 (Navy oscuro)
```

### Gradientes predefinidos

```javascript
gradients.header      // Azul → Magenta
gradients.background  // Navy degradado
gradients.button      // Azul claro
gradients.accent      // Magenta claro
```

### Sombras (elevation)

```javascript
shadows.sm            // Sombra pequeña
shadows.md            // Sombra media
shadows.lg            // Sombra grande
shadows.xl            // Sombra extra grande
```

## Variables CSS (más fácil aún)

Si prefieres usar CSS variables directamente (recomendado):

```css
/* En App.module.css o cualquier .css */
.container {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: var(--color-text-primary);
  box-shadow: var(--shadow-lg);
}
```

Todas las variables están en `frontend/src/styles/variables.css`.

---

**Dopamina = Éxito.** 🎨
