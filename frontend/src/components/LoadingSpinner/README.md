# ⏳ LoadingSpinner

Componente de carga elegante que se muestra mientras el backend procesa.

## Estructura

```
LoadingSpinner/
├── LoadingSpinner.jsx          # Lógica del componente
├── LoadingSpinner.module.css   # Estilos con BEM
└── README.md                   # Este archivo
```

## Props

**No recibe props.** Es un componente presentacional puro.

## Ejemplo de uso

```jsx
import LoadingSpinner from './components/LoadingSpinner/LoadingSpinner';

function App() {
  const [loading, setLoading] = useState(false);

  return (
    <>
      {loading && <LoadingSpinner />}
    </>
  );
}
```

## Características

- 🎯 **Mensajes aleatorios** - Cada vez que se carga dice algo diferente
- ✨ **Animación elegante** - Tres círculos rebotadores
- 📝 **Mensajes informativos** - Explica qué está pasando
- 🎨 **Tema editorial** - Colores cálidos y literarios

## Mensajes

Muestra uno aleatorio de estos:
- "Analizando reseñas..."
- "Extrayendo emociones con BERT..."
- "Calculando similitud..."
- "Encontrando joyas ocultas..."
- "Casi listo..."

## CSS Classes (BEM)

### Block: `.spinner`
- `.spinner` - Contenedor principal

### Elements:
- `.spinner__container` - Wrapper centrado
- `.spinner__animation` - Contenedor de circles
- `.spinner__circle` - Cada circle que rebota
- `.spinner__text` - Texto y mensajes
- `.spinner__message` - Mensaje principal
- `.spinner__hint` - Hint secundario

## Animaciones

- **Bounce**: Círculos rebotan en secuencia
- **Pulse**: Texto parpadea suavemente

## Responsividad

- **Desktop** (> 768px): Tamaño grande
- **Tablet** (640-768px): Tamaño medio
- **Mobile** (< 640px): Tamaño pequeño y compacto

## Mejoras posibles

- [ ] Mostrar progreso si se sabe cuántos pasos hay
- [ ] Agregar más variedad de mensajes
- [ ] Permitir pasar mensaje personalizado como prop
- [ ] Agregar sound si el usuario lo permite
- [ ] Cancelar carga con botón

## Notas para estudiantes

Este es un componente **puramente presentacional**:
- No gestiona estado
- No hace llamadas a API
- Solo renderiza la UI
- El padre (App.jsx) maneja cuándo mostrarlo

Es un buen ejemplo de componente **dumb component** que solo recibe props
(aunque en este caso no recibe ninguno).
