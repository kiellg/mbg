import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Alert, Box, Button, Chip, CircularProgress,
  Paper, Stack, Typography,
} from '@mui/material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { adminApi } from '../../api/admin';

function getApiError(error, fallback = 'Request failed') {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || fallback).join(', ');
  }

  return detail || fallback;
}

function CountCard({ label, value, helper }) {
  return (
    <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
      <Typography variant="overline" color="text.secondary" sx={{ letterSpacing: '0.06em' }}>
        {label}
      </Typography>
      <Typography variant="h4" sx={{ mt: 0.75, fontFamily: '"Playfair Display", serif' }}>
        {value}
      </Typography>
      {helper && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75 }}>
          {helper}
        </Typography>
      )}
    </Paper>
  );
}

function requireArray(data, label) {
  if (Array.isArray(data)) {
    return data;
  }

  throw new Error(`Unexpected ${label} response format.`);
}

function requireObject(data, label) {
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    return data;
  }

  throw new Error(`Unexpected ${label} response format.`);
}

export default function AdminDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [userCount, setUserCount] = useState(0);
  const [couponCount, setCouponCount] = useState(0);
  const [roleCounts, setRoleCounts] = useState({});

  useEffect(() => {
    let active = true;

    const loadDashboard = async () => {
      setLoading(true);
      setError(null);

      try {
        const [analyticsResponse, usersResponse, couponsResponse] = await Promise.all([
          adminApi.getOrderAnalytics(),
          adminApi.getUsers(),
          adminApi.listCoupons(),
        ]);

        if (!active) {
          return;
        }

        const analyticsData = requireObject(analyticsResponse.data, 'analytics');
        const users = requireArray(usersResponse.data, 'users');
        const coupons = requireArray(couponsResponse.data, 'coupons');
        const roleBreakdown = users.reduce((counts, user) => {
          const role = user.role || 'unknown';
          counts[role] = (counts[role] || 0) + 1;
          return counts;
        }, {});

        setAnalytics(analyticsData);
        setUserCount(users.length);
        setCouponCount(coupons.length);
        setRoleCounts(roleBreakdown);
      } catch (err) {
        if (!active) {
          return;
        }

        setError(getApiError(err, 'Failed to load dashboard data'));
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadDashboard();
    return () => {
      active = false;
    };
  }, []);

  const statusEntries = Object.entries(analytics?.orders_by_status || {});
  const roleEntries = Object.entries(roleCounts);

  return (
    <DashboardLayout contentMaxWidth={1180}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, alignItems: { xs: 'flex-start', md: 'center' }, flexDirection: { xs: 'column', md: 'row' } }}>
          <Box>
            <Typography variant="h4" sx={{ fontFamily: '"Playfair Display", serif', mb: 0.5 }}>
              Admin dashboard
            </Typography>
            <Typography color="text.secondary">
              Quick view of orders, users, and coupon activity.
            </Typography>
          </Box>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
            <Button component={RouterLink} to="/admin/users" variant="outlined">
              Manage users
            </Button>
            <Button component={RouterLink} to="/admin/coupons" variant="contained">
              Manage coupons
            </Button>
          </Stack>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        {loading ? (
          <Paper elevation={0} sx={{ p: 4, borderRadius: 3, display: 'flex', justifyContent: 'center' }}>
            <CircularProgress />
          </Paper>
        ) : (
          <>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, minmax(0, 1fr))', xl: 'repeat(5, minmax(0, 1fr))' }, gap: 2 }}>
              <CountCard label="Total orders" value={analytics?.total_orders ?? 0} />
              <CountCard label="Orders today" value={analytics?.orders_today ?? 0} />
              <CountCard label="Orders this week" value={analytics?.orders_this_week ?? 0} />
              <CountCard label="Users" value={userCount} />
              <CountCard label="Coupons" value={couponCount} />
            </Box>

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1.2fr 0.8fr' }, gap: 2 }}>
              <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="h6" sx={{ mb: 2, fontFamily: '"Playfair Display", serif' }}>
                  Order status breakdown
                </Typography>

                {statusEntries.length === 0 ? (
                  <Typography color="text.secondary">No orders yet.</Typography>
                ) : (
                  <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                    {statusEntries.map(([status, count]) => (
                      <Chip key={status} label={`${status}: ${count}`} variant="outlined" />
                    ))}
                  </Stack>
                )}
              </Paper>

              <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="h6" sx={{ mb: 2, fontFamily: '"Playfair Display", serif' }}>
                  Users by role
                </Typography>

                {roleEntries.length === 0 ? (
                  <Typography color="text.secondary">No users found.</Typography>
                ) : (
                  <Stack spacing={1.25}>
                    {roleEntries.map(([role, count]) => (
                      <Box key={role} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography sx={{ textTransform: 'capitalize' }}>{role}</Typography>
                        <Chip label={count} size="small" />
                      </Box>
                    ))}
                  </Stack>
                )}
              </Paper>
            </Box>
          </>
        )}
      </Box>
    </DashboardLayout>
  );
}
