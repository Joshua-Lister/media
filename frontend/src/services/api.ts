/**
 * API service for making HTTP requests to the backend.
 *
 * **IMPORTANT: Update API URL**
 * The API URL is configured via environment variable:
 * Create a .env file in the frontend directory with:
 * REACT_APP_API_URL=http://localhost:8000
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config;

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);

          // Retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    apiClient.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    apiClient.post('/auth/login', data),

  refresh: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
};

// Articles API
export const articlesAPI = {
  list: (params?: { page?: number; limit?: number; category?: string }) =>
    apiClient.get('/articles', { params }),

  get: (id: string) =>
    apiClient.get(`/articles/${id}`),

  create: (data: any) =>
    apiClient.post('/articles', data),

  update: (id: string, data: any) =>
    apiClient.put(`/articles/${id}`, data),

  delete: (id: string) =>
    apiClient.delete(`/articles/${id}`),

  search: (query: string) =>
    apiClient.get('/articles/search', { params: { q: query } }),
};

// Topics API
export const topicsAPI = {
  list: (params?: { category?: string; tags?: string; search?: string }) =>
    apiClient.get('/topics/', { params }),

  recommended: () =>
    apiClient.get('/topics/recommended'),

  trending: () =>
    apiClient.get('/topics/trending'),

  create: (data: { title: string; description: string; category?: string }) =>
    apiClient.post('/topics', data),

  vote: (id: string, voteType: 'upvote' | 'downvote') =>
    apiClient.post(`/topics/${id}/vote`, { vote_type: voteType }),
};

// Users API
export const usersAPI = {
  getProfile: () =>
    apiClient.get('/users/profile'),

  updateProfile: (data: any) =>
    apiClient.put('/users/profile', data),

  toggleMode: () =>
    apiClient.post('/users/toggle-mode'),
};

// Payments API
export const paymentsAPI = {
  createSubscription: (data: any) =>
    apiClient.post('/payments/subscribe', data),

  donate: (data: any) =>
    apiClient.post('/payments/donate', data),

  getEarnings: () =>
    apiClient.get('/payments/earnings'),

  getPublishableKey: () =>
    apiClient.get('/payments/publishable-key'),
};

// Ratings API
export const ratingsAPI = {
  create: (articleId: string, data: {
    rating: number;
    feedback?: string;
    accuracy_rating?: number;
    sources_rating?: number;
    writing_quality_rating?: number;
    originality_rating?: number;
    depth_rating?: number;
    bias_rating?: number;
  }) =>
    apiClient.post(`/articles/${articleId}/ratings`, data),

  list: (articleId: string) =>
    apiClient.get(`/articles/${articleId}/ratings`),
};

// Annotations API
export const annotationsAPI = {
  create: (articleId: string, data: {
    selection_text: string;
    selection_start_offset: number;
    selection_end_offset: number;
    annotation_type: string;
    comment: string;
    evidence_url?: string;
    evidence_title?: string;
    evidence_excerpt?: string;
  }) =>
    apiClient.post(`/articles/${articleId}/annotations`, data),

  list: (articleId: string) =>
    apiClient.get(`/articles/${articleId}/annotations`),

  vote: (annotationId: string, voteType: 'upvote' | 'downvote') =>
    apiClient.post(`/annotations/${annotationId}/vote`, { vote_type: voteType }),
};

// AI API
export const aiAPI = {
  generateArticle: (data: { topic: string; keywords?: string[]; tone?: string; length?: string }) =>
    apiClient.post('/ai/generate-article', data),

  improveDraft: (data: { title: string; content: string; feedback?: string }) =>
    apiClient.post('/ai/improve-draft', data),

  summarize: (content: string) =>
    apiClient.post('/ai/summarize', { content }),
};

export default apiClient;
