import api from './axios';

export const cartApi = {
    getCart: (restaurantId) =>
        api.get(`/cart/${restaurantId}`),

    addItem: (restaurantId, payload) =>
        api.post(`/cart/${restaurantId}/items`, payload),

    updateItem: (restaurantId, itemId, payload) =>
        api.put(`/cart/${restaurantId}/items/${itemId}`, payload),

    removeItem: (restaurantId, itemId) =>
        api.delete(`/cart/${restaurantId}/items/${itemId}`),
};
