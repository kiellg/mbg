import api from "./axios";

export const authApi = {
    register: (name, email, password, role) =>
        api.post('/auth/register', { name, email, password, role }),

    login: (email, password) =>
        api.post('/auth/login', { email, password }),

    logout: () =>
        api.post('/auth/logout'),

    getMe: () =>
        api.get('/auth/me'),

    forgotPassword: (email) =>
        api.post('/auth/forgot-password', { email }),

    resetPassword: (token, new_password) =>
        api.post('/auth/reset-password', { token, new_password }),
};