import api from './axios';

export const favouritesApi = {
    getAll: () => api.get('/favourites'),
    add: (target_id, target_type, restaurant_id = null) =>
        api.post('/favourites', { target_id, target_type, restaurant_id }),
    remove: (targetId, targetType, restaurantId = null) =>
        api.delete('/favourites', { params: {
            target_id: targetId,
            target_type: targetType,
            ...(restaurantId != null && { restaurant_id: restaurantId }),
        }}),
};