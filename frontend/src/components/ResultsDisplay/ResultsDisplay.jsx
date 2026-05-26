import React from 'react';
import styles from './ResultsDisplay.module.css';
import EmotionRadar from '../EmotionRadar/EmotionRadar';
import EmotionBars from '../EmotionBars/EmotionBars';
import MetricPill from '../MetricPill/MetricPill';
import BookCard from '../BookCard/BookCard';

function ResultsDisplay({ recommendations }) {
  const baseBook = recommendations?.libro_base;
  const books = recommendations?.recomendaciones || [];

  if (!baseBook) {
    return null;
  }

  return (
    <section className={styles.results}>
      <div className={styles.basePanel}>
        <div className={styles.baseText}>
          <span className={styles.kicker}>Libro base</span>

          <h2>{baseBook.book_title || 'Título desconocido'}</h2>

          <p className={styles.author}>
            {baseBook.author || 'Autor desconocido'}
          </p>

          <div className={styles.metrics}>
            <MetricPill
              label="Dominante"
              value={
                baseBook.emocion_dominante_es ||
                baseBook.emocion_dominante ||
                '—'
              }
            />

            <MetricPill
              label="Rating"
              value={Number(baseBook.average_rating || 0).toFixed(2)}
            />

            <MetricPill
              label="Sentimiento"
              value={Number(baseBook.average_sentiment || 0).toFixed(2)}
            />
          </div>

          {baseBook.genres && (
            <p className={styles.genres}>
              {String(baseBook.genres)}
            </p>
          )}

          {baseBook.book_details && (
            <div className={styles.synopsisBox}>
              <span className={styles.synopsisTitle}>Sinopsis</span>
              <p className={styles.synopsis}>
                {String(baseBook.book_details)}
              </p>
            </div>
          )}

          <EmotionBars profile={baseBook} />
        </div>

        <div className={styles.radarPanel}>
          <EmotionRadar profile={baseBook} />
        </div>
      </div>

      <div className={styles.sectionHeader}>
        <div>
          <span className={styles.kicker}>Ruta de lectura</span>
          <h2>Libros recomendados</h2>
        </div>

        <p>
          {books.length} resultados ordenados por score final.
        </p>
      </div>

      {books.length === 0 ? (
        <div className={styles.emptyState}>
          <strong>No hay recomendaciones disponibles</strong>
          <p>
            Prueba con otro título o revisa que el backend esté devolviendo datos.
          </p>
        </div>
      ) : (
        <div className={styles.cards}>
          {books.map((book, index) => (
            <BookCard
              key={`${book.book_id || book.book_title}-${index}`}
              book={book}
              position={index + 1}
            />
          ))}
        </div>
      )}
    </section>
  );
}

export default ResultsDisplay;