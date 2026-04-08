import api from './axios';

export const favouritesApi = {
    getAll: () => api.get('/favourites'),
    add: (target_id, target_type, restaurant_id = null) =>
        api.post('/favourites', { target_id, target_type, restaurant_id }),
    remove: (target_id, target_type) =>
        api.delete(`/favourites/${target_id}`, { params: { target_type } }),
};