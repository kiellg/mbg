import { useState } from 'react';
import { Link } from 'react-router-dom';
import { TextField, Button, Alert, Box, Typography, Paper } from '@mui/material';
import { KeyOutlined } from '@mui/icons-material';
import AuthLayout from '../../components/shared/AuthLayout';
import { useAuth } from '../../context/AuthContext';

export default function ForgotPasswordPage() {
  const { forgotPassword, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [resetToken, setResetToken] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    setResetToken(null);
    const result = await forgotPassword(email);
    if (result.success) {
      setFeedback({ type: 'success', message: 'Token generated successfully.' });
      setResetToken(result.reset_token);
    } else {
      setFeedback({ type: 'error', message: result.message });
    }
  };

  return (
    <AuthLayout title="Forgot password?" subtitle="Enter your email and we'll generate a reset token">
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}

        {resetToken && (
          <Paper elevation={0} sx={{ p: 2, borderRadius: 3, border: '1px dashed', borderColor: 'primary.main', bgcolor: 'rgba(192,57,43,0.04)' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <KeyOutlined sx={{ fontSize: 16, color: 'primary.main' }} />
              <Typography variant="body2" fontWeight={600} color="primary.main">Your reset token</Typography>
            </Box>
            <Typography variant="body2"
              sx={{ fontFamily: 'monospace', fontSize: '0.75rem', wordBreak: 'break-all', color: 'text.secondary', lineHeight: 1.6 }}>
              {resetToken}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
              Copy this and use it on the{' '}
              <Typography component={Link} to="/reset-password" variant="caption"
                sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                Reset password
              </Typography>{' '}page. Expires in 1 hour.
            </Typography>
          </Paper>
        )}

        <TextField label="Email address" name="email" type="email" autoComplete="email"
          value={email} onChange={(e) => setEmail(e.target.value)} required />

        <Button type="submit" variant="contained" fullWidth disabled={loading}>
          {loading ? 'Sending…' : 'Send reset token'}
        </Button>

        <Typography variant="body2" textAlign="center" color="text.secondary">
          <Typography component={Link} to="/login" variant="body2"
            sx={{ color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
            ← Back to login
          </Typography>
        </Typography>
      </Box>
    </AuthLayout>
  );
}