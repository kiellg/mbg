import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { notificationsApi } from '../api/notifications';
import { useAuth } from './AuthContext';

const NotificationsContext = createContext(null);
const SUPPORTED_ROLES = new Set(['customer', 'manager', 'driver']);

function getApiError(error, fallback = 'Request failed') {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || fallback).join(', ');
  }

  return detail || fallback;
}

function sortNotifications(items) {
  return [...items].sort((left, right) => {
    const leftTimestamp = new Date(left.timestamp).getTime();
    const rightTimestamp = new Date(right.timestamp).getTime();
    return rightTimestamp - leftTimestamp;
  });
}

export function NotificationsProvider({ children }) {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const loadedUserKeyRef = useRef(null);

  const clearNotifications = useCallback(() => {
    loadedUserKeyRef.current = null;
    setNotifications([]);
    setLoading(false);
    setError(null);
  }, []);

  const refreshNotifications = useCallback(async ({ force = true } = {}) => {
    const role = user?.role;
    const userId = user?.user_id;

    if (!userId || !SUPPORTED_ROLES.has(role)) {
      clearNotifications();
      return { success: true, data: [] };
    }

    const nextUserKey = `${role}:${userId}`;
    if (!force && loadedUserKeyRef.current === nextUserKey) {
      return { success: true };
    }

    setLoading(true);
    setError(null);

    try {
      const { data } = await notificationsApi.listNotifications();
      const nextNotifications = sortNotifications(data || []);
      loadedUserKeyRef.current = nextUserKey;
      setNotifications(nextNotifications);
      return { success: true, data: nextNotifications };
    } catch (err) {
      const message = getApiError(err, 'Failed to load notifications');
      setError(message);
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  }, [clearNotifications, user?.role, user?.user_id]);

  const markNotificationAsRead = useCallback(async (notificationId) => {
    const role = user?.role;
    const userId = user?.user_id;

    if (!userId || !SUPPORTED_ROLES.has(role)) {
      clearNotifications();
      return { success: false, message: 'Notifications are unavailable for this role.' };
    }

    setError(null);

    try {
      const { data } = await notificationsApi.markAsRead(notificationId);
      setNotifications((currentNotifications) => currentNotifications.map((notification) => (
        notification.notification_id === notificationId
          ? { ...notification, ...data }
          : notification
      )));
      return { success: true, data };
    } catch (err) {
      const message = getApiError(err, 'Failed to update notification');
      setError(message);
      return { success: false, message };
    }
  }, [clearNotifications, user?.role, user?.user_id]);

  useEffect(() => {
    const role = user?.role;
    const userId = user?.user_id;

    if (!userId || !SUPPORTED_ROLES.has(role)) {
      clearNotifications();
      return;
    }

    const nextUserKey = `${role}:${userId}`;
    if (loadedUserKeyRef.current === nextUserKey) {
      return;
    }

    refreshNotifications({ force: false });
  }, [clearNotifications, refreshNotifications, user?.role, user?.user_id]);

  const unreadCount = notifications.reduce((count, notification) => (
    notification.is_read ? count : count + 1
  ), 0);

  return (
    <NotificationsContext.Provider
      value={{
        notifications,
        loading,
        error,
        unreadCount,
        refreshNotifications,
        markNotificationAsRead,
        clearNotifications,
      }}
    >
      {children}
    </NotificationsContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error('useNotifications must be used inside NotificationsProvider');
  }

  return context;
}
