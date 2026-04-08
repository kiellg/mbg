import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, Button, Alert,
  CircularProgress, Divider, RadioGroup, FormControlLabel,
  Radio, TextField, Stack
} from '@mui/material';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { paymentApi } from '../../api/payment';

export default function PaymentPage() {
  const { orderId } = useParams();
  const navigate = useNavigate();

  const [savedMethods, setSavedMethods]   = useState([]);
  const [selectedMethod, setSelectedMethod] = useState('new'); // 'new' or savedMethod id
  const [cardNumber, setCardNumber]       = useState('');
  const [expiry, setExpiry]               = useState('');
  const [cvv, setCvv]                     = useState('');
  const [loading, setLoading]             = useState(false);
  const [fetchingMethods, setFetchingMethods] = useState(true);
  const [error, setError]                 = useState(null);
  const [receipt, setReceipt]             = useState(null); // success state

  // Load saved payment methods on mount
  useEffect(() => {
    paymentApi.getMethods()
      .then(({ data }) => setSavedMethods(data))
      .catch(() => {}) // silently fail — new card form is fallback
      .finally(() => setFetchingMethods(false));
  }, []);

  const handlePay = async () => {
    setLoading(true); setError(null);
    try {
      if (selectedMethod !== 'new') {
        // Pay with saved method
        await paymentApi.payWithSaved(orderId, selectedMethod);
      } else {
        // Pay with new card
        await paymentApi.processPayment(orderId, {
          card_number: cardNumber,
          expiry,
          cvv,
        });
      }
      // Fetch receipt on success
      const { data } = await paymentApi.getReceipt(orderId);
      setReceipt(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Payment failed. Please try again.');
    } finally { setLoading(false); }
  };

  // ── Receipt / Success Screen ──────────────────────────────
  if (receipt) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default',
        display: 'flex', alignItems: 'center', justifyContent: 'center', px: 2 }}>
        <Card sx={{ maxWidth: 480, width: '100%', textAlign: 'center' }}>
          <CardContent sx={{ py: 5 }}>
            <CheckCircleOutlineIcon sx={{ fontSize: 64, color: '#C0392B', mb: 2 }} />
            <Typography variant="h2" sx={{ fontSize: '1.6rem', color: '#1C2833', mb: 1 }}>
              Order Confirmed!
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Order #{receipt.order_id} · Total: ${receipt.total?.toFixed(2)}
            </Typography>
            <Divider sx={{ mb: 3, borderColor: '#EDE5D8' }} />
            <Button variant="contained" color="primary"
              onClick={() => navigate('/')}>
              Back to Home
            </Button>
          </CardContent>
        </Card>
      </Box>
    );
  }

  // ── Payment Form ──────────────────────────────────────────
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', px: { xs: 2, sm: 4 }, py: 5 }}>
      <Box sx={{ maxWidth: 560, mx: 'auto' }}>

        {/* Header */}
        <Typography variant="h2" sx={{ mb: 1, fontSize: '2rem', color: '#1C2833' }}>
          Payment
        </Typography>
        <Box sx={{ height: 4, width: 48,
          background: 'linear-gradient(90deg, #C0392B, #E74C3C)',
          borderRadius: 2, mb: 4 }} />

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        {/* Saved methods */}
        {!fetchingMethods && savedMethods.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h4" sx={{ mb: 2, fontSize: '1rem', fontWeight: 600 }}>
                Saved Cards
              </Typography>
              <RadioGroup value={selectedMethod}
                onChange={(e) => setSelectedMethod(e.target.value)}>
                {savedMethods.map((m) => (
                  <FormControlLabel key={m.id} value={String(m.id)}
                    control={<Radio color="primary" />}
                    label={`•••• •••• •••• ${m.last4} — ${m.brand}`} />
                ))}
                <FormControlLabel value="new"
                  control={<Radio color="primary" />}
                  label="Use a new card" />
              </RadioGroup>
            </CardContent>
          </Card>
        )}

        {/* New card form */}
        {selectedMethod === 'new' && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                <CreditCardIcon sx={{ color: '#C0392B' }} />
                <Typography variant="h4" sx={{ fontSize: '1rem', fontWeight: 600 }}>
                  Card Details
                </Typography>
              </Stack>

              <Stack spacing={2}>
                <TextField fullWidth size="small" label="Card Number"
                  placeholder="1234 5678 9012 3456"
                  value={cardNumber} onChange={(e) => setCardNumber(e.target.value)}
                  inputProps={{ maxLength: 19 }} />
                <Stack direction="row" spacing={2}>
                  <TextField fullWidth size="small" label="Expiry (MM/YY)"
                    placeholder="MM/YY"
                    value={expiry} onChange={(e) => setExpiry(e.target.value)} />
                  <TextField fullWidth size="small" label="CVV"
                    placeholder="123"
                    value={cvv} onChange={(e) => setCvv(e.target.value)}
                    inputProps={{ maxLength: 4 }} />
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        )}

        <Button variant="contained" color="primary" fullWidth size="large"
          disabled={loading} onClick={handlePay}>
          {loading ? <CircularProgress size={22} color="inherit" /> : `Pay Now`}
        </Button>

      </Box>
    </Box>
  );
}