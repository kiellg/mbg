import api from './axios';

export const paymentApi = {
  getMethods:     ()                         => api.get('/payments/methods'),
  saveMethod:     (payload)                  => api.post('/payments/methods', payload),
  processPayment: (orderId, payload)         => api.post(`/payments/${orderId}`, payload),
  payWithSaved:   (orderId, savedMethodId)   => api.post(`/payments/${orderId}/saved/${savedMethodId}`),
  getReceipt:     (orderId)                  => api.get(`/payments/${orderId}/receipt`),
};