# 🦄 App - Componente raíz

Contenedor principal de la aplicación.

## Estructura

```
app/
├── App.jsx              # Componente raíz
├── App.module.css       # Estilos (BEM)
└── README.md           # Este archivo
```

## Props

No recibe props. Es el punto de entrada.

## Responsabilidades

- Gestión de estado global (recommendations, loading, error)
- Orquestación de componentes
- Llamadas a API (`/recommend`)
- Layout principal (header, main, footer)

## Estructura de estado

```javascript
const [recommendations, setRecommendations] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [originalBook, setOriginalBook] = useState('');
```

## API calls

```javascript
// POST /recommend
const response = await axios.post(`${API_URL}/recommend`, {
  title: bookTitle,
  description: description
});
```

## Flujo de datos

```
App (estado)
├─ RecommendationForm (entrada)
├─ LoadingSpinner (while loading)
└─ ResultsDisplay (salida)
    └─ BookCard × 5
```

---

Del Unicornio que se piró. 🦄
