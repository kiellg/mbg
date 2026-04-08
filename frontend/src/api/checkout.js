import api from './axios';

export const checkoutApi = {
  checkout: (restaurantId, payload) => api.post(`/checkout/${restaurantId}`, payload),
  // payload: { delivery_method: 'delivery' | 'pickup', coupon_code: 'OPTIONAL' }
};