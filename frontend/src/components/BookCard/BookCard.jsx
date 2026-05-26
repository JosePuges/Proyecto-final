import React from 'react';
import styles from './BookCard.module.css';
import EmotionBars from '../EmotionBars/EmotionBars';

function pct(v) {
  return `${Math.round(Number(v || 0) * 100)}%`;
}

function BookCard({ book, position }) {
  const score = Number(book.score_final ?? book.similarity ?? 0);

  return (
    <article className={styles.card}>
      <div className={styles.top}>
        <div className={styles.rank}>#{position}</div>

        <div className={styles.match}>
          <span>{Math.round(score * 100)}%</span>
          match
        </div>
      </div>

      <div className={styles.content}>
        <h3>{book.book_title || 'Título desconocido'}</h3>

        <p className={styles.author}>
          {book.author || 'Autor desconocido'}
        </p>

        <div className={styles.grid}>
          <div>
            <span>Dominante</span>
            <strong>
              {book.emocion_dominante_es || book.emocion_dominante || '—'}
            </strong>
          </div>

          <div>
            <span>Rating</span>
            <strong>{Number(book.average_rating || 0).toFixed(2)}</strong>
          </div>

          <div>
            <span>Emoción</span>
            <strong>{pct(book.emotion_similarity ?? book.similarity)}</strong>
          </div>

          <div>
            <span>Géneros</span>
            <strong>{pct(book.genre_similarity)}</strong>
          </div>
        </div>

        <EmotionBars profile={book} />

        {book.genres && (
          <p className={styles.genres}>
            {String(book.genres)}
          </p>
        )}

        {book.book_details && (
          <div className={styles.synopsisBox}>
            <span className={styles.synopsisTitle}>Sinopsis</span>
            <p className={styles.synopsis}>
              {String(book.book_details)}
            </p>
          </div>
        )}

        {book.reason && (
          <p className={styles.reason}>
            {book.reason}
          </p>
        )}
      </div>
    </article>
  );
}

export default BookCard;