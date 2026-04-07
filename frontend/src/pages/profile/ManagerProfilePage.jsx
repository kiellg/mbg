import { useState } from 'react';
import { TextField, Button, Alert, Box, Typography, InputAdornment } from '@mui/material';
import { SaveOutlined, StoreOutlined, StarOutlined } from '@mui/icons-material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import ProfileSection from '../../components/shared/ProfileSection';
import { profileApi } from '../../api/profile';
import { useAuth } from '../../context/AuthContext';

export default function ManagerProfilePage() {
  const { user } = useAuth();
  const [restaurantId, setRestaurantId] = useState('');
  const [form, setForm] = useState({ name: '', address: '', rating: '', opening_hours: '' });
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [saved, setSaved] = useState(null);

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    const id = parseInt(restaurantId, 10);
    if (!restaurantId || isNaN(id)) {
      setFeedback({ type: 'warning', message: 'Please enter a valid restaurant ID.' });
      return;
    }
    const payload = {};
    if (form.name.trim())          payload.name = form.name.trim();
    if (form.address.trim())       payload.address = form.address.trim();
    if (form.opening_hours.trim()) payload.opening_hours = form.opening_hours.trim();
    if (form.rating !== '') {
      const r = parseInt(form.rating, 10);
      if (isNaN(r) || r < 1 || r > 5) {
        setFeedback({ type: 'warning', message: 'Rating must be between 1 and 5.' });
        return;
      }
      payload.rating = r;
    }
    if (!Object.keys(payload).length) {
      setFeedback({ type: 'warning', message: 'Enter at least one field to update.' });
      return;
    }
    setSaving(true);
    try {
      const { data } = await profileApi.updateRestaurant(id, payload);
      setSaved(data);
      setFeedback({ type: 'success', message: data.message });
      setForm({ name: '', address: '', rating: '', opening_hours: '' });
    } catch (err) {
      setFeedback({ type: 'error', message: err.response?.data?.detail || 'Update failed' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3.5 }}>
        <Box sx={{ width: 40, height: 40, borderRadius: 2.5, bgcolor: 'rgba(26,82,118,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <StoreOutlined sx={{ color: '#1A5276', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography variant="h4" sx={{ fontSize: '1.4rem', lineHeight: 1.2 }}>Restaurant Profile</Typography>
          <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
        </Box>
      </Box>

      {saved && (
        <ProfileSection title="Last saved" description="Server response from the most recent update">
          <Box>
            {[
              { label: 'Restaurant ID', value: saved.restaurant_id },
              { label: 'Name',          value: saved.name },
              { label: 'Address',       value: saved.address },
              { label: 'Rating',        value: saved.rating ? `${saved.rating} / 5` : '—' },
              { label: 'Opening hours', value: saved.opening_hours },
            ].map(({ label, value }) => (
              <Box key={label} sx={{ display: 'flex', gap: 2, py: 0.9, borderBottom: '0.5px solid', borderColor: 'divider', '&:last-child': { border: 'none' } }}>
                <Typography variant="body2" color="text.secondary" sx={{ width: 140, flexShrink: 0 }}>{label}</Typography>
                <Typography variant="body2" fontWeight={500}>{value ?? '—'}</Typography>
              </Box>
            ))}
          </Box>
        </ProfileSection>
      )}

      <ProfileSection title="Select restaurant" description="Enter the ID of the restaurant you manage">
        <TextField label="Restaurant ID" value={restaurantId} onChange={(e) => setRestaurantId(e.target.value)}
          placeholder="e.g. 1" type="number" inputProps={{ min: 1 }} sx={{ maxWidth: 220 }} />
      </ProfileSection>

      <ProfileSection title="Update restaurant details" description="Leave fields blank to keep their current values">
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}
          <TextField label="Restaurant name" name="name" value={form.name} onChange={handleChange} placeholder="The Golden Fork" />
          <TextField label="Address" name="address" value={form.address} onChange={handleChange}
            placeholder="456 Restaurant Row, Vancouver, BC" multiline minRows={2} />
          <TextField label="Rating" name="rating" value={form.rating} onChange={handleChange}
            placeholder="1–5" type="number" inputProps={{ min: 1, max: 5 }} sx={{ maxWidth: 180 }}
            InputProps={{ endAdornment: <InputAdornment position="end"><StarOutlined sx={{ fontSize: 16, color: 'text.secondary' }} /></InputAdornment> }} />
          <TextField label="Opening hours" name="opening_hours" value={form.opening_hours} onChange={handleChange}
            placeholder="Mon–Fri 11:00–22:00, Sat–Sun 10:00–23:00" />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button type="submit" variant="contained" disabled={saving} startIcon={<SaveOutlined />} sx={{ minWidth: 140 }}>
              {saving ? 'Saving…' : 'Save changes'}
            </Button>
          </Box>
        </Box>
      </ProfileSection>
    </DashboardLayout>
  );
}