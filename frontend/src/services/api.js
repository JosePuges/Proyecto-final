import axios from 'axios';
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const apiClient = axios.create({ baseURL: API_URL, timeout: 25000 });
export async function getEmotionalRecommendations({ title, topN = 5, minReviews = 1, excluirMismoAutor = false }) {
  const response = await apiClient.get('/recommendations/emotional', {
    params: { title, top_n: topN, min_reviews: minReviews, excluir_mismo_autor: excluirMismoAutor },
  });
  return response.data;
}
export default apiClient;
