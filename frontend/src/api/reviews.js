import api from './axios';

export const reviewsApi = {
  submit: (payload) => api.post('/reviews', payload),
  // payload: { order_id: str, rating: int, comment: str | null }

  getForRestaurant: (restaurantId) =>
    api.get(`/reviews/restaurant/${restaurantId}`),
};