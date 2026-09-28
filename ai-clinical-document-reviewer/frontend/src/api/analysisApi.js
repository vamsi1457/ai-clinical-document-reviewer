import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for OCR/LLM processing
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let customMessage = 'An unexpected network error occurred.';
    if (error.response?.data?.error?.message) {
      customMessage = error.response.data.error.message;
    } else if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      customMessage = typeof detail === 'string' ? detail : detail.message || JSON.stringify(detail);
    } else if (error.message) {
      customMessage = error.message;
    }
    return Promise.reject(new Error(customMessage));
  }
);

export const analysisApi = {
  /**
   * Submit raw clinical text for AI review.
   */
  async submitText(text) {
    const response = await apiClient.post('/analyses', { text }, {
      headers: { 'Content-Type': 'application/json' },
    });
    return response.data;
  },

  /**
   * Submit document file (PDF, PNG, JPG, JPEG) for AI review.
   */
  async submitFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/analyses', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /**
   * Fetch previous clinical analyses with optional search and status filter.
   */
  async listAnalyses(params = {}) {
    const response = await apiClient.get('/analyses', { params });
    return response.data;
  },

  /**
   * Fetch complete clinical report by ID.
   */
  async getAnalysisById(id) {
    const response = await apiClient.get(`/analyses/${id}`);
    return response.data;
  },

  /**
   * Delete an analysis report by ID.
   */
  async deleteAnalysis(id) {
    const response = await apiClient.delete(`/analyses/${id}`);
    return response.data;
  },

  /**
   * Backend health check.
   */
  async checkHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default analysisApi;
