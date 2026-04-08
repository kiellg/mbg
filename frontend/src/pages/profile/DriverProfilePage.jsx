import { useState, useEffect, useCallback } from 'react';
import {
  TextField, Button, Alert, Box, Typography,
  FormControl, InputLabel, Select, MenuItem,
  Switch, FormControlLabel, Skeleton, Chip,
} from '@mui/material';
import { SaveOutlined, TwoWheelerOutlined, RefreshOutlined } from '@mui/icons-material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import ProfileSection from '../../components/shared/ProfileSection';
import { profileApi } from '../../api/profile';
import { useAuth } from '../../context/AuthContext';

const DELIVERY_METHODS = [
  { value: 'walk',       label: '� Walking'     },
  { value: 'bike',       label: '🚴 Bicycle'    },
  { value: 'car',        label: '🚗 Car'         },
];

export default function DriverProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState(null);
  const [form, setForm] = useState({ name: '', delivery_method: '', is_available: false });
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const fetchProfile = useCallback(async () => {
    setProfileLoading(true);
    setProfileError(null);
    try {
      const { data } = await profileApi.getDriver();
      setProfile(data);
      setForm({ name: data.name || '', delivery_method: data.delivery_method || '', is_available: data.is_available ?? false });
    } catch (err) {
      setProfileError(err.response?.data?.detail || 'Failed to load profile');
    } finally {
      setProfileLoading(false);
    }
  }, []);

  useEffect(() => { fetchProfile(); }, [fetchProfile]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    const payload = {};
    if (form.name.trim() && form.name !== profile?.name)                         payload.name = form.name.trim();
    if (form.delivery_method && form.delivery_method !== profile?.delivery_method) payload.delivery_method = form.delivery_method;
    if (form.is_available !== profile?.is_available)                              payload.is_available = form.is_available;
    if (!Object.keys(payload).length) {
      setFeedback({ type: 'info', message: 'No changes detected.' });
      return;
    }
    setSaving(true);
    try {
      const { data } = await profileApi.updateDriver(payload.name, payload.delivery_method, payload.is_available);
      setProfile(data);
      setFeedback({ type: 'success', message: data.message });
    } catch (err) {
      setFeedback({ type: 'error', message: err.response?.data?.detail || 'Update failed' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3.5 }}>
        <Box sx={{ width: 40, height: 40, borderRadius: 2.5, bgcolor: 'rgba(30,132,73,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <TwoWheelerOutlined sx={{ color: '#1E8449', fontSize: 20 }} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" sx={{ fontSize: '1.4rem', lineHeight: 1.2 }}>Driver Profile</Typography>
          <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
        </Box>
        <Button size="small" startIcon={<RefreshOutlined />} onClick={fetchProfile} disabled={profileLoading}>Refresh</Button>
      </Box>

      <ProfileSection title="Current status" description="Live values from the server">
        {profileLoading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>{[1,2,3].map(i => <Skeleton key={i} height={28} />)}</Box>
        ) : profileError ? (
          <Alert severity="error">{profileError}</Alert>
        ) : profile && (
          <Box>
            {[
              { label: 'Name', value: profile.name },
              { label: 'Delivery method', value: DELIVERY_METHODS.find(m => m.value === profile.delivery_method)?.label || profile.delivery_method },
              { label: 'Availability', value: (
                <Chip label={profile.is_available ? 'Available' : 'Unavailable'} size="small"
                  sx={{ bgcolor: profile.is_available ? 'rgba(30,132,73,0.12)' : 'rgba(0,0,0,0.06)', color: profile.is_available ? '#1E8449' : 'text.secondary', fontWeight: 600, fontSize: '0.75rem', height: 22 }} />
              )},
            ].map(({ label, value }) => (
              <Box key={label} sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 0.9, borderBottom: '0.5px solid', borderColor: 'divider', '&:last-child': { border: 'none' } }}>
                <Typography variant="body2" color="text.secondary" sx={{ width: 140, flexShrink: 0 }}>{label}</Typography>
                <Typography variant="body2" fontWeight={500} component="span">{value}</Typography>
              </Box>
            ))}
          </Box>
        )}
      </ProfileSection>

      <ProfileSection title="Update profile" description="Only changed fields are sent to the server">
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}
          <TextField label="Name" value={form.name} onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))} />
          <FormControl fullWidth size="small">
            <InputLabel>Delivery method</InputLabel>
            <Select label="Delivery method" value={form.delivery_method}
              onChange={(e) => setForm(p => ({ ...p, delivery_method: e.target.value }))}
              sx={{ borderRadius: 2.5, bgcolor: '#FDFBF8' }}>
              {DELIVERY_METHODS.map(m => <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControlLabel
            control={<Switch checked={form.is_available ?? false} onChange={(e) => setForm(p => ({ ...p, is_available: e.target.checked }))} color="success" />}
            label={
              <Box>
                <Typography variant="body2" fontWeight={500}>Available for deliveries</Typography>
                <Typography variant="caption" color="text.secondary">Toggle off to stop receiving new orders</Typography>
              </Box>
            }
          />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button type="submit" variant="contained" disabled={saving || profileLoading} startIcon={<SaveOutlined />} sx={{ minWidth: 140 }}>
              {saving ? 'Saving…' : 'Save changes'}
            </Button>
          </Box>
        </Box>
      </ProfileSection>
    </DashboardLayout>
  );
}