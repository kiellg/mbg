import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  TextField, Button, Alert, Box, Typography,
  InputAdornment, IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import AuthLayout from '../../components/shared/AuthLayout';
import { useAuth } from '../../context/AuthContext';

export default function ResetPasswordPage() {
  const { resetPassword, loading } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ token: '', new_password: '' });
  const [showPw, setShowPw] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    const result = await resetPassword(form.token, form.new_password);
    if (result.success) {
      setFeedback({ type: 'success', message: result.message + ' Redirecting to login…' });
      setTimeout(() => navigate('/login'), 1500);
    } else {
      setFeedback({ type: 'error', message: result.message });
    }
  };

  return (
    <AuthLayout title="Set new password" subtitle="Paste your reset token and choose a new password">
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}

        <TextField label="Reset token" name="token" value={form.token} onChange={handleChange}
          placeholder="Paste your token here"
          inputProps={{ style: { fontFamily: 'monospace', fontSize: '0.8rem' } }} required />

        <TextField
          label="New password" name="new_password" type={showPw ? 'text' : 'password'}
          autoComplete="new-password" value={form.new_password} onChange={handleChange} required
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton size="small" onClick={() => setShowPw((v) => !v)} edge="end">
                  {showPw ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Button type="submit" variant="contained" fullWidth disabled={loading}>
          {loading ? 'Resetting…' : 'Reset password'}
        </Button>

        <Typography variant="body2" textAlign="center" color="text.secondary">
          Don't have a token?{' '}
          <Typography component={Link} to="/forgot-password" variant="body2"
            sx={{ color: 'primary.main', textDecoration: 'none', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}>
            Request one
          </Typography>
        </Typography>
      </Box>
    </AuthLayout>
  );
}