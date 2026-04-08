import api from './axios';

export const profileApi = {
    getCustomer: () =>
        api.get('/profile/customer'),

    updateCustomer: (name, delivery_address) =>
        api.patch('/profile/customer', { name, delivery_address }),

    getDriver: () =>
        api.get('/profile/driver'),

    updateDriver : (name, delivery_method, is_available) =>
        api.patch('/profile/driver', { name, delivery_method, is_available }),

    updateRestaurant: (restaurant_id, payload) =>
        api.patch(`/profile/restaurant/${restaurant_id}`, payload),
};