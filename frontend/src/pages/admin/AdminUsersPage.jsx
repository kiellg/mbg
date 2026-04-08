import { useEffect, useState } from 'react';
import {
  Alert, Box, Button, Chip, CircularProgress, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Typography,
} from '@mui/material';
import DeleteOutlineOutlined from '@mui/icons-material/DeleteOutlineOutlined';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { adminApi } from '../../api/admin';

function getApiError(error, fallback = 'Request failed') {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || fallback).join(', ');
  }

  return detail || fallback;
}

function getRoleChipColor(role) {
  if (role === 'customer') return 'warning';
  if (role === 'manager') return 'info';
  if (role === 'driver') return 'success';
  return 'default';
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [busyUserId, setBusyUserId] = useState(null);

  useEffect(() => {
    let active = true;

    const loadUsers = async () => {
      setLoading(true);
      setError(null);

      try {
        const { data } = await adminApi.getUsers();
        if (!active) {
          return;
        }

        setUsers(data || []);
      } catch (err) {
        if (!active) {
          return;
        }

        setError(getApiError(err, 'Failed to load users'));
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadUsers();
    return () => {
      active = false;
    };
  }, []);

  const handleDelete = async (user) => {
    if (user.role === 'admin') {
      return;
    }

    const confirmed = window.confirm(`Delete ${user.email}?`);
    if (!confirmed) {
      return;
    }

    setBusyUserId(user.user_id);
    setFeedback(null);
    setError(null);

    try {
      await adminApi.deleteUser(user.user_id);
      setUsers((currentUsers) => currentUsers.filter((currentUser) => currentUser.user_id !== user.user_id));
      setFeedback({ type: 'success', message: `Deleted ${user.email}.` });
    } catch (err) {
      setError(getApiError(err, 'Failed to delete user'));
    } finally {
      setBusyUserId(null);
    }
  };

  return (
    <DashboardLayout contentMaxWidth={1180}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontFamily: '"Playfair Display", serif', mb: 0.5 }}>
            User management
          </Typography>
          <Typography color="text.secondary">
            View all users and remove non-admin accounts.
          </Typography>
        </Box>

        {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}
        {error && <Alert severity="error">{error}</Alert>}

        {loading ? (
          <Paper elevation={0} sx={{ p: 4, borderRadius: 3, display: 'flex', justifyContent: 'center' }}>
            <CircularProgress />
          </Paper>
        ) : (
          <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4}>
                      <Typography color="text.secondary">No users found.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  users.map((user) => {
                    const isAdmin = user.role === 'admin';
                    const isBusy = busyUserId === user.user_id;

                    return (
                      <TableRow key={user.user_id} hover>
                        <TableCell>{user.name || 'Unnamed user'}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>
                          <Chip label={user.role || 'unknown'} color={getRoleChipColor(user.role)} size="small" sx={{ textTransform: 'capitalize' }} />
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            color="error"
                            size="small"
                            startIcon={isBusy ? <CircularProgress size={16} color="inherit" /> : <DeleteOutlineOutlined />}
                            disabled={isAdmin || isBusy}
                            onClick={() => handleDelete(user)}
                          >
                            {isAdmin ? 'Protected' : 'Delete'}
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </DashboardLayout>
  );
}
