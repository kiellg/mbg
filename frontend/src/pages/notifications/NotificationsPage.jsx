import { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import NotificationsOutlined from '@mui/icons-material/NotificationsOutlined';
import RefreshOutlined from '@mui/icons-material/RefreshOutlined';
import MarkEmailReadOutlined from '@mui/icons-material/MarkEmailReadOutlined';
import LaunchOutlined from '@mui/icons-material/LaunchOutlined';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationsContext';

function formatTimestamp(timestamp) {
  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) {
    return timestamp || 'Unknown time';
  }

  return parsed.toLocaleString();
}

function getNotificationDestination(role, notification) {
  if (!notification?.order_id) {
    return null;
  }

  if (role === 'customer') {
    return {
      to: '/orders',
      label: 'View orders',
    };
  }

  if (role === 'driver') {
    return {
      to: '/deliveries',
      label: 'View deliveries',
    };
  }

  return null;
}

export default function NotificationsPage() {
  const { user } = useAuth();
  const {
    notifications,
    loading,
    error,
    unreadCount,
    refreshNotifications,
    markNotificationAsRead,
  } = useNotifications();
  const [busyNotificationId, setBusyNotificationId] = useState(null);

  const handleRefresh = async () => {
    await refreshNotifications();
  };

  const handleMarkAsRead = async (notificationId) => {
    setBusyNotificationId(notificationId);
    await markNotificationAsRead(notificationId);
    setBusyNotificationId(null);
  };

  return (
    <DashboardLayout contentMaxWidth={980}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, alignItems: { xs: 'flex-start', sm: 'center' }, flexDirection: { xs: 'column', sm: 'row' } }}>
          <Box>
            <Typography variant="h4" sx={{ fontFamily: '"Playfair Display", serif', mb: 0.5 }}>
              Notifications
            </Typography>
            <Typography color="text.secondary">
              {unreadCount > 0
                ? `${unreadCount} unread notification${unreadCount === 1 ? '' : 's'}`
                : 'Latest order and delivery updates for your account.'}
            </Typography>
          </Box>

          <Button
            variant="outlined"
            onClick={handleRefresh}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <RefreshOutlined />}
          >
            Refresh
          </Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {loading && notifications.length === 0 ? (
          <Paper elevation={0} sx={{ p: 4, borderRadius: 3, display: 'flex', justifyContent: 'center' }}>
            <CircularProgress />
          </Paper>
        ) : notifications.length === 0 ? (
          <Paper elevation={0} sx={{ p: 5, borderRadius: 3, border: '1px solid', borderColor: 'divider', textAlign: 'center' }}>
            <NotificationsOutlined sx={{ fontSize: 44, color: 'text.disabled', mb: 1 }} />
            <Typography variant="h6" sx={{ mb: 1 }}>
              No notifications yet
            </Typography>
            <Typography color="text.secondary">
              Notifications will appear here after order, payment, and delivery activity.
            </Typography>
          </Paper>
        ) : (
          <Stack spacing={2}>
            {notifications.map((notification) => {
              const destination = getNotificationDestination(user?.role, notification);
              const isUnread = !notification.is_read;
              const isBusy = busyNotificationId === notification.notification_id;

              return (
                <Paper
                  key={notification.notification_id}
                  elevation={0}
                  sx={{
                    p: 2.5,
                    borderRadius: 3,
                    border: '1px solid',
                    borderColor: isUnread ? 'rgba(192,57,43,0.25)' : 'divider',
                    bgcolor: isUnread ? 'rgba(192,57,43,0.04)' : 'background.paper',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, alignItems: { xs: 'flex-start', sm: 'center' }, flexDirection: { xs: 'column', sm: 'row' }, mb: 1.5 }}>
                    <Stack direction="row" spacing={1} alignItems="center" useFlexGap flexWrap="wrap">
                      <Chip
                        label={isUnread ? 'Unread' : 'Read'}
                        color={isUnread ? 'primary' : 'default'}
                        variant={isUnread ? 'filled' : 'outlined'}
                        size="small"
                      />
                      {notification.order_id && (
                        <Chip label={`Order #${notification.order_id}`} size="small" variant="outlined" />
                      )}
                    </Stack>

                    <Typography variant="caption" color="text.secondary">
                      {formatTimestamp(notification.timestamp)}
                    </Typography>
                  </Box>

                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {notification.message}
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {destination && (
                      <Button
                        component={RouterLink}
                        to={destination.to}
                        size="small"
                        variant="outlined"
                        startIcon={<LaunchOutlined />}
                      >
                        {destination.label}
                      </Button>
                    )}

                    {isUnread && (
                      <Button
                        size="small"
                        variant="contained"
                        onClick={() => handleMarkAsRead(notification.notification_id)}
                        disabled={isBusy}
                        startIcon={isBusy ? <CircularProgress size={16} color="inherit" /> : <MarkEmailReadOutlined />}
                      >
                        Mark as read
                      </Button>
                    )}
                  </Box>
                </Paper>
              );
            })}
          </Stack>
        )}
      </Box>
    </DashboardLayout>
  );
}
