import { useState } from 'react';
import { TextField, Button, Alert, Box, Typography } from '@mui/material';
import { SaveOutlined, PersonOutlined } from '@mui/icons-material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import ProfileSection from '../../components/shared/ProfileSection';
import { profileApi } from '../../api/profile';
import { useAuth } from '../../context/AuthContext';

export default function CustomerProfilePage() {
  const { user } = useAuth();
  const [form, setForm] = useState({ name: '', delivery_address: '' });
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [saved, setSaved] = useState(null);

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    const payload = {};
    if (form.name.trim())             payload.name = form.name.trim();
    if (form.delivery_address.trim()) payload.delivery_address = form.delivery_address.trim();
    if (!Object.keys(payload).length) {
      setFeedback({ type: 'warning', message: 'Enter at least one field to update.' });
      return;
    }
    setLoading(true);
    try {
      const { data } = await profileApi.updateCustomer(payload.name, payload.delivery_address);
      setSaved(data);
      setFeedback({ type: 'success', message: data.message });
      setForm({ name: '', delivery_address: '' });
    } catch (err) {
      setFeedback({ type: 'error', message: err.response?.data?.detail || 'Update failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3.5 }}>
        <Box sx={{ width: 40, height: 40, borderRadius: 2.5, bgcolor: 'rgba(192,57,43,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <PersonOutlined sx={{ color: '#C0392B', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography variant="h4" sx={{ fontSize: '1.4rem', lineHeight: 1.2 }}>My Profile</Typography>
          <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
        </Box>
      </Box>

      {saved && (
        <ProfileSection title="Current info" description="Last saved values from the server">
          <Box>
            {[{ label: 'Name', value: saved.name }, { label: 'Delivery address', value: saved.delivery_address }].map(({ label, value }) => (
              <Box key={label} sx={{ display: 'flex', gap: 2, py: 0.75, borderBottom: '0.5px solid', borderColor: 'divider', '&:last-child': { border: 'none' } }}>
                <Typography variant="body2" color="text.secondary" sx={{ width: 140, flexShrink: 0 }}>{label}</Typography>
                <Typography variant="body2" fontWeight={500}>{value || '—'}</Typography>
              </Box>
            ))}
          </Box>
        </ProfileSection>
      )}

      <ProfileSection title="Update profile" description="Leave a field blank to keep its current value">
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}
          <TextField label="Name" name="name" value={form.name} onChange={handleChange} placeholder="Your display name" />
          <TextField label="Delivery address" name="delivery_address" value={form.delivery_address} onChange={handleChange}
            placeholder="123 Main St, Vancouver, BC" multiline minRows={2} />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button type="submit" variant="contained" disabled={loading} startIcon={<SaveOutlined />} sx={{ minWidth: 140 }}>
              {loading ? 'Saving…' : 'Save changes'}
            </Button>
          </Box>
        </Box>
      </ProfileSection>
    </DashboardLayout>
  );
}