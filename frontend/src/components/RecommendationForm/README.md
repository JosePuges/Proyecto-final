# 🎯 RecommendationForm

Componente que captura la búsqueda del usuario y envía la solicitud al backend.

## Estructura

```
RecommendationForm/
├── RecommendationForm.jsx          # Lógica del componente
├── RecommendationForm.module.css   # Estilos con BEM
└── README.md                       # Este archivo
```

## Props

| Prop | Tipo | Descripción |
|------|------|-------------|
| `onSubmit` | `function(bookTitle, description)` | Callback ejecutado cuando usuario envía el formulario |
| `disabled` | `boolean` | Si `true`, deshabilita los inputs (útil mientras se procesa) |

## Ejemplo de uso

```jsx
import RecommendationForm from './components/RecommendationForm/RecommendationForm';

function App() {
  const handleSubmit = async (title, description) => {
    // Enviar al backend
    const response = await fetch('/api/recommend', {
      method: 'POST',
      body: JSON.stringify({ title, description })
    });
  };

  return (
    <RecommendationForm 
      onSubmit={handleSubmit}
      disabled={false}
    />
  );
}
```

## Estado interno

- **bookTitle**: string - Título del libro que busca el usuario
- **description**: string - Descripción breve de por qué le gustó

## CSS Classes (BEM)

### Block: `.form`
- `.form` - Contenedor principal

### Elements:
- `.form__header` - Encabezado con título y subtítulo
- `.form__title` - H2 del formulario
- `.form__subtitle` - Texto descriptivo pequeño
- `.form__content` - Contenedor de campos
- `.form__group` - Grupo de label + input
- `.form__label` - Labels de inputs
- `.form__input` - Input text
- `.form__textarea` - Textarea
- `.form__hint` - Texto de ayuda bajo campo
- `.form__button` - Botón de envío
- `.form__info` - Caja de información al pie

### Modifiers:
- `.form__button--loading` - Estado cuando está procesando

## Validación

- ✅ **Title** es obligatorio (required)
- ✅ Botón está deshabilitado si title está vacío
- ✅ Botón está deshabilitado si prop `disabled={true}`

## Responsividad

- **Desktop** (> 768px): Formulario completo
- **Tablet** (640-768px): Padding reducido, font sizes ajustados
- **Mobile** (< 640px): Padding menor, font sizes más pequeños

## Variables CSS usadas

Del archivo `src/styles/variables.css`:
- `--color-primary` - Color principal (marrón)
- `--color-bg-primary` - Color de fondo
- `--color-text-primary` - Color de texto
- `--border-radius-md` - Bordes redondeados
- `--shadow-md`, `--shadow-lg` - Sombras

## Mejoras posibles

- [ ] Validación de título (máximo caracteres)
- [ ] Auto-complete de títulos desde dataset
- [ ] Historial de búsquedas recientes
- [ ] Guardar "favoritos" de búsquedas
