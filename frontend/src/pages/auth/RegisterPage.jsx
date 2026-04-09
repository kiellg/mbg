import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  TextField, Button, Alert, Box, Typography,
  InputAdornment, IconButton, Divider, Paper,
} from '@mui/material';
import { Visibility, VisibilityOff, CheckCircle } from '@mui/icons-material';
import AuthLayout from '../../components/shared/AuthLayout';
import { useAuth } from '../../context/AuthContext';

const ROLES = [
  { value: 'customer', label: 'Customer', emoji: '🛍️', desc: 'Order delicious food' },
  { value: 'manager',  label: 'Manager',  emoji: '🏪', desc: 'Manage a restaurant'  },
  { value: 'driver',   label: 'Driver',   emoji: '🚴', desc: 'Deliver orders'       },
];

export default function RegisterPage() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'customer' });
  const [showPw, setShowPw] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    const result = await register(form.name, form.email, form.password, form.role);
    if (result.success) {
      setFeedback({ type: 'success', message: 'Account created! Redirecting to login…' });
      setTimeout(() => navigate('/login'), 1200);
    } else {
      setFeedback({ type: 'error', message: result.message });
    }
  };

  return (
    <AuthLayout title="Create account" subtitle="Join Chow — it only takes a moment">
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}

        <TextField label="Full name" name="name" autoComplete="name" value={form.name} onChange={handleChange} required />
        <TextField label="Email address" name="email" type="email" autoComplete="email" value={form.email} onChange={handleChange} required />

        <TextField
          label="Password" name="password" type={showPw ? 'text' : 'password'}
          autoComplete="new-password" value={form.password} onChange={handleChange} required
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

        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>I am a…</Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 1 }}>
            {ROLES.map((r) => {
              const selected = form.role === r.value;
              return (
                <Paper key={r.value} onClick={() => setForm((p) => ({ ...p, role: r.value }))} elevation={0}
                  sx={{
                    p: 1.5, textAlign: 'center', cursor: 'pointer',
                    border: '1.5px solid', borderColor: selected ? 'primary.main' : 'divider',
                    borderRadius: 3, bgcolor: selected ? 'rgba(192,57,43,0.06)' : 'background.paper',
                    transition: 'all 0.15s', position: 'relative', userSelect: 'none',
                    '&:hover': { borderColor: 'primary.main', bgcolor: 'rgba(192,57,43,0.04)' },
                  }}
                >
                  {selected && <CheckCircle sx={{ position: 'absolute', top: 6, right: 6, fontSize: 14, color: 'primary.main' }} />}
                  <Typography sx={{ fontSize: '1.4rem', lineHeight: 1, mb: 0.5 }}>{r.emoji}</Typography>
                  <Typography variant="body2" fontWeight={600} color={selected ? 'primary.main' : 'text.primary'}>{r.label}</Typography>
                  <Typography variant="caption" color="text.secondary" display="block">{r.desc}</Typography>
                </Paper>
              );
            })}
          </Box>
        </Box>

        <Button type="submit" variant="contained" fullWidth disabled={loading}>
          {loading ? 'Creating account…' : 'Create account'}
        </Button>

        <Divider sx={{ my: 0.5 }}>
          <Typography variant="body2" color="text.secondary" sx={{ px: 1 }}>or</Typography>
        </Divider>

        <Typography variant="body2" textAlign="center" color="text.secondary">
          Already have an account?{' '}
          <Typography component={Link} to="/login" variant="body2"
            sx={{ color: 'primary.main', textDecoration: 'none', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}>
            Sign in
          </Typography>
        </Typography>
      </Box>
    </AuthLayout>
  );
}