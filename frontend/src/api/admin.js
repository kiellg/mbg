import api from './axios';

export const adminApi = {
  getUsers: () =>
    api.get('/admin/users'),

  deleteUser: (userId) =>
    api.delete(`/admin/users/${userId}`),

  getOrderAnalytics: () =>
    api.get('/admin/analytics/orders'),

  listCoupons: () =>
    api.get('/admin/coupons'),

  getCoupon: (couponCode) =>
    api.get(`/admin/coupons/${couponCode}`),

  createCoupon: (payload) =>
    api.post('/admin/coupons', payload),

  updateCoupon: (couponCode, payload) =>
    api.patch(`/admin/coupons/${couponCode}`, payload),

  deactivateCoupon: (couponCode) =>
    api.patch(`/admin/coupons/${couponCode}/deactivate`),

  deleteCoupon: (couponCode) =>
    api.delete(`/admin/coupons/${couponCode}`),
};
