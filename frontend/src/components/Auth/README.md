# Auth Component

## Login.jsx

Componente de login/register.

**Props:**
- `onLoginSuccess(email, token)` - Callback cuando login es exitoso

**Comportamiento:**
- Toggle entre login y register
- Almacena token en localStorage
- Estados de carga y error

**Uso:**
```jsx
import Login from './Auth/Login';

<Login onLoginSuccess={(email, token) => {
  setToken(token);
}} />
```

## Login.module.css

Estilos BEM para el componente.

Clases disponibles:
- `.auth-container` - Contenedor principal
- `.auth-form` - Formulario
- `.auth-input` - Inputs de email/password
- `.auth-button` - Botón submit
- `.auth-toggle` - Botón para cambiar login/register
- `.auth-error` - Mensaje de error

