import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  TextField, Button, Alert, Box, Typography,
  InputAdornment, IconButton, Divider,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import AuthLayout from '../../components/shared/AuthLayout';
import { useAuth } from '../../context/AuthContext';

export default function LoginPage() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: '', password: '' });
  const [showPw, setShowPw] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    const result = await login(form.email, form.password);
    if (result.success) {
      setFeedback({ type: 'success', message: result.message });
      setTimeout(() => navigate('/me'), 600);
    } else {
      setFeedback({ type: 'error', message: result.message });
    }
  };

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to your Bitewave account">
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}

        <TextField label="Email address" name="email" type="email"
          autoComplete="email" value={form.email} onChange={handleChange} required />

        <TextField
          label="Password" name="password" type={showPw ? 'text' : 'password'}
          autoComplete="current-password" value={form.password} onChange={handleChange} required
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

        <Box sx={{ textAlign: 'right', mt: -1 }}>
          <Typography component={Link} to="/forgot-password" variant="body2"
            sx={{ color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
            Forgot password?
          </Typography>
        </Box>

        <Button type="submit" variant="contained" fullWidth disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </Button>

        <Divider sx={{ my: 0.5 }}>
          <Typography variant="body2" color="text.secondary" sx={{ px: 1 }}>or</Typography>
        </Divider>

        <Typography variant="body2" textAlign="center" color="text.secondary">
          Don't have an account?{' '}
          <Typography component={Link} to="/register" variant="body2"
            sx={{ color: 'primary.main', textDecoration: 'none', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}>
            Create one
          </Typography>
        </Typography>
      </Box>
    </AuthLayout>
  );
}