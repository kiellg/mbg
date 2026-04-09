import api from './axios';

export const notificationsApi = {
  listNotifications: () =>
    api.get('/notifications'),

  markAsRead: (notificationId) =>
    api.patch(`/notifications/${notificationId}/read`),
};
