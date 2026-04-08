import api from './axios';

export const restaurantApi = {
    // Restaurants
    getAll: () =>
        api.get('/restaurants'),
    getAllPaginated: (page = 1, limit = 10, sort_by = 'rating', order = 'desc') =>
        api.get('/restaurants/paginated/sorted', { params: { page, limit, sort_by, order } }),
    getMenu: (restaurantId) =>
        api.get(`/restaurants/${restaurantId}/menu`),
    getMenuPaginated: (restaurantId, page = 1, limit = 10, sort_by = 'price', order = 'asc') =>
        api.get(`/restaurants/${restaurantId}/menu/paginated/sorted`, { params: { page, limit, sort_by, order } }),
    create: (payload) =>
        api.post('/restaurants', payload),
    update: (restaurantId, payload) =>
        api.patch(`/restaurants/${restaurantId}`, payload),
    delete: (restaurantId) =>
        api.delete(`/restaurants/${restaurantId}`),

    // Menu items
    getMenuItem: (restaurantId, itemId) =>
        api.get(`/restaurants/${restaurantId}/menu/${itemId}`),
    createMenuItem: (restaurantId, payload) =>
        api.post(`/restaurants/${restaurantId}/menu`, payload),
    updateMenuItem: (restaurantId, itemId, payload) =>
        api.patch(`/restaurants/${restaurantId}/menu/${itemId}`, payload),
    deleteMenuItem: (restaurantId, itemId) =>
        api.delete(`/restaurants/${restaurantId}/menu/${itemId}`),

    // Search & filter
    search: (q) =>
        api.get('/restaurants/search', { params: { q } }),
    searchMenuItems: (q) =>
        api.get('/restaurants/menu/search', { params: { q } }),
    getSuggestions: (q) =>
        api.get('/restaurants/search/suggestions', { params: { q } }),
    filter: (cuisine_types) =>
        api.get('/restaurants/filter', { params: { cuisine_types } }),
    getCategories: () =>
        api.get('/restaurants/categories'),
};