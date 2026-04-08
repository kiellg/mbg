import api from './axios';

export const ordersApi = {
  getAll: () => api.get('/orders'),
};