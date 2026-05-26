import { useState } from 'react';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const endpoint = isLogin ? '/auth/login' : '/auth/register';

    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || 'Error al conectar');
        return;
      }

      const data = await response.json();
      onLoginSuccess(email, data.access_token);
    } catch (err) {
      setError('Error de conexión con el backend');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '100px auto', padding: '2rem',
      background: '#1a1a2e', borderRadius: '12px', color: 'white' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
        🦄 {isLogin ? 'Iniciar sesión' : 'Registrarse'}
      </h2>

      {error && <p style={{ color: '#ff6b6b', marginBottom: '1rem' }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          style={{ width: '100%', padding: '10px', marginBottom: '1rem',
            borderRadius: '6px', border: 'none', boxSizing: 'border-box' }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Contraseña"
          required
          style={{ width: '100%', padding: '10px', marginBottom: '1rem',
            borderRadius: '6px', border: 'none', boxSizing: 'border-box' }}
        />
        <button type="submit"
          style={{ width: '100%', padding: '12px', background: '#6C3FC5',
            color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer',
            fontWeight: 'bold', fontSize: '1rem' }}>
          {isLogin ? 'Entrar' : 'Crear cuenta'}
        </button>
      </form>

      <button onClick={() => setIsLogin(!isLogin)}
        style={{ width: '100%', marginTop: '1rem', padding: '10px',
          background: 'transparent', color: '#aaa', border: '1px solid #444',
          borderRadius: '6px', cursor: 'pointer' }}>
        {isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Entra'}
      </button>
    </div>
  );
}