import pickle
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
CACHE_PATH = os.path.join(DATA_PATH, 'emotion_profiles.csv')
MODEL_PATH = os.path.join('cache', 'naive_bayes_emotions.pkl')
EMOTIONS = ['joy', 'sadness', 'fear', 'surprise', 'anger', 'disgust']

df = pd.read_csv(CACHE_PATH)
df = df.dropna(subset=EMOTIONS)
df['dominant_emotion'] = df[EMOTIONS].idxmax(axis=1)

X = df[EMOTIONS].values
y = df['dominant_emotion'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = GaussianNB()
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"✓ Modelo guardado en {MODEL_PATH}")