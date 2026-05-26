import React, { useState, useEffect, useRef } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function UserMenu({ token, onLogout }) {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState('menu'); // menu | perfil | review | historial
  const [user, setUser] = useState(null);
  const [msg, setMsg] = useState('');
  const menuRef = useRef(null);

  // Cargar datos del usuario al abrir
  useEffect(() => {
    if (open && !user) {
      fetch(`${API_URL}/user/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(r => r.json())
        .then(data => setUser(data))
        .catch(() => {});
    }
  }, [open, user, token]);

  // Cerrar el menu al hacer clic fuera
  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
        setView('menu');
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // ESTILOS inline
  const styles = {
    wrapper: { position: 'fixed', top: '20px', right: '20px', zIndex: 1000 },
    avatar: {
      width: '44px', height: '44px', borderRadius: '50%', cursor: 'pointer',
      background: 'linear-gradient(135deg, #6C3FC5, #C04AC5)', color: 'white',
      border: 'none', fontWeight: 'bold', fontSize: '1.1rem'
    },
    dropdown: {
      position: 'absolute', top: '54px', right: '0', width: '300px',
      background: '#1a1a2e', borderRadius: '12px', padding: '1rem',
      boxShadow: '0 8px 30px rgba(0,0,0,0.5)', color: 'white'
    },
    item: {
      display: 'block', width: '100%', padding: '12px', marginBottom: '4px',
      background: 'transparent', color: 'white', border: 'none',
      textAlign: 'left', cursor: 'pointer', borderRadius: '6px', fontSize: '0.95rem'
    },
    input: {
      width: '100%', padding: '10px', marginBottom: '0.8rem', borderRadius: '6px',
      border: 'none', boxSizing: 'border-box'
    },
    btn: {
      width: '100%', padding: '10px', background: '#6C3FC5', color: 'white',
      border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
    },
    back: {
      background: 'transparent', color: '#aaa', border: 'none',
      cursor: 'pointer', marginBottom: '0.8rem', padding: 0
    },
    title: { margin: '0 0 1rem 0', fontSize: '1.1rem' },
    msg: { color: '#7ee787', fontSize: '0.85rem', marginTop: '0.5rem' }
  };

  const inicial = user?.username
    ? user.username[0].toUpperCase()
    : (user?.email ? user.email[0].toUpperCase() : '?');

  return (
    <div style={styles.wrapper} ref={menuRef}>
      <button style={styles.avatar} onClick={() => setOpen(!open)}>
        {inicial}
      </button>

      {open && (
        <div style={styles.dropdown}>

          {/* VISTA MENU */}
          {view === 'menu' && (
            <>
              <p style={{ margin: '0 0 0.8rem 0', fontSize: '0.85rem', color: '#aaa' }}>
                {user?.username || user?.email || 'Cargando...'}
              </p>
              <button style={styles.item} onClick={() => setView('perfil')}>👤 Perfil</button>
              <button style={styles.item} onClick={() => setView('review')}>✍️ Añadir reseña</button>
              <button style={styles.item} onClick={() => setView('historial')}>🕘 Historial</button>
              <button style={{ ...styles.item, color: '#ff6b6b' }} onClick={onLogout}>
                🚪 Cerrar sesión
              </button>
            </>
          )}

          {/* VISTA PERFIL */}
          {view === 'perfil' && (
            <Perfil token={token} user={user} setUser={setUser}
                    onBack={() => { setView('menu'); setMsg(''); }} styles={styles} />
          )}

          {/* VISTA AÑADIR RESEÑA */}
          {view === 'review' && (
            <AddReview token={token} onBack={() => setView('menu')} styles={styles} />
          )}

          {/* VISTA HISTORIAL */}
          {view === 'historial' && (
            <Historial onBack={() => setView('menu')} styles={styles} />
          )}

        </div>
      )}
    </div>
  );
}

// ---------- SUBCOMPONENTE: PERFIL ----------
function Perfil({ token, user, setUser, onBack, styles }) {
  const [username, setUsername] = useState(user?.username || '');
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [msg, setMsg] = useState('');

  async function guardarUsername() {
    setMsg('');
    try {
      const r = await fetch(`${API_URL}/user/username`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ username })
      });
      if (!r.ok) { setMsg('Error al guardar'); return; }
      setUser({ ...user, username });
      setMsg('Nombre actualizado ✓');
    } catch {
      setMsg('Error de conexión');
    }
  }

  async function guardarPassword() {
    setMsg('');
    try {
      const r = await fetch(`${API_URL}/user/password`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ current_password: currentPw, new_password: newPw })
      });
      if (!r.ok) {
        const d = await r.json();
        setMsg(d.detail || 'Error al cambiar contraseña');
        return;
      }
      setCurrentPw(''); setNewPw('');
      setMsg('Contraseña actualizada ✓');
    } catch {
      setMsg('Error de conexión');
    }
  }

  return (
    <>
      <button style={styles.back} onClick={onBack}>← Volver</button>
      <h3 style={styles.title}>Perfil</h3>
      <p style={{ fontSize: '0.85rem', color: '#aaa' }}>Email: {user?.email}</p>

      <p style={{ fontSize: '0.85rem', marginBottom: '0.4rem' }}>Nombre de usuario</p>
      <input style={styles.input} value={username}
             onChange={e => setUsername(e.target.value)} placeholder="Tu nombre" />
      <button style={styles.btn} onClick={guardarUsername}>Guardar nombre</button>

      <p style={{ fontSize: '0.85rem', margin: '1rem 0 0.4rem 0' }}>Cambiar contraseña</p>
      <input style={styles.input} type="password" value={currentPw}
             onChange={e => setCurrentPw(e.target.value)} placeholder="Contraseña actual" />
      <input style={styles.input} type="password" value={newPw}
             onChange={e => setNewPw(e.target.value)} placeholder="Nueva contraseña" />
      <button style={styles.btn} onClick={guardarPassword}>Cambiar contraseña</button>

      {msg && <p style={styles.msg}>{msg}</p>}
    </>
  );
}

// ---------- SUBCOMPONENTE: AÑADIR RESEÑA ----------
function AddReview({ token, onBack, styles }) {
  const [bookTitle, setBookTitle] = useState('');
  const [reviewText, setReviewText] = useState('');
  const [rating, setRating] = useState(5);
  const [msg, setMsg] = useState('');

  async function enviar() {
    setMsg('');
    try {
      const r = await fetch(`${API_URL}/user/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          book_title: bookTitle,
          review_text: reviewText,
          rating: parseInt(rating)
        })
      });
      if (!r.ok) { setMsg('Error al guardar la reseña'); return; }
      setBookTitle(''); setReviewText(''); setRating(5);
      setMsg('Reseña guardada ✓');
    } catch {
      setMsg('Error de conexión');
    }
  }

  return (
    <>
      <button style={styles.back} onClick={onBack}>← Volver</button>
      <h3 style={styles.title}>Añadir reseña</h3>
      <input style={styles.input} value={bookTitle}
             onChange={e => setBookTitle(e.target.value)} placeholder="Título del libro" />
      <textarea style={{ ...styles.input, minHeight: '80px', resize: 'vertical' }}
                value={reviewText} onChange={e => setReviewText(e.target.value)}
                placeholder="Tu reseña..." />
      <select style={styles.input} value={rating} onChange={e => setRating(e.target.value)}>
        <option value={1}>1 - Muy malo</option>
        <option value={2}>2 - Malo</option>
        <option value={3}>3 - Normal</option>
        <option value={4}>4 - Bueno</option>
        <option value={5}>5 - Excelente</option>
      </select>
      <button style={styles.btn} onClick={enviar}>Guardar reseña</button>
      {msg && <p style={styles.msg}>{msg}</p>}
    </>
  );
}

// ---------- SUBCOMPONENTE: HISTORIAL ----------
function Historial({ onBack, styles }) {
  const historial = JSON.parse(localStorage.getItem('searchHistory') || '[]');

  return (
    <>
      <button style={styles.back} onClick={onBack}>← Volver</button>
      <h3 style={styles.title}>Historial de búsquedas</h3>
      {historial.length === 0 ? (
        <p style={{ fontSize: '0.85rem', color: '#aaa' }}>
          Todavía no has buscado nada.
        </p>
      ) : (
        historial.slice().reverse().map((item, i) => (
          <p key={i} style={{
            fontSize: '0.9rem', padding: '8px', background: '#0f0f1e',
            borderRadius: '6px', marginBottom: '4px'
          }}>
            📖 {item}
          </p>
        ))
      )}
    </>
  );
}
