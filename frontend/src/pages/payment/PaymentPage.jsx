import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, Button, Alert,
  CircularProgress, Divider, RadioGroup, FormControlLabel,
  Radio, TextField, Stack
} from '@mui/material';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { paymentApi } from '../../api/payment';
import { checkoutApi } from '../../api/checkout';

export default function PaymentPage() {
  const { orderId }  = useParams();
  const navigate     = useNavigate();
  const location     = useLocation();

  // Order passed from CheckoutPage via navigate state.
  // Fall back to fetching from the API so the summary survives a page refresh.
  const [order, setOrder] = useState(location.state?.order ?? null);

  const [savedMethods, setSavedMethods]         = useState([]);
  const [selectedMethod, setSelectedMethod]     = useState('new');
  const [cardNumber, setCardNumber]             = useState('');
  const [expiryDate, setExpiryDate]             = useState('');
  const [cvv, setCvv]                           = useState('');
  const [cardholderName, setCardholderName]     = useState('');
  const [loading, setLoading]                   = useState(false);
  const [fetchingMethods, setFetchingMethods]   = useState(true);
  const [error, setError]                       = useState(null);
  const [receipt, setReceipt]                   = useState(null);

  // If the user refreshed or navigated directly, re-fetch order details
  useEffect(() => {
    if (!order && orderId) {
      checkoutApi.getOrder(orderId)
        .then(({ data }) => setOrder(data))
        .catch(() => {}); // non-fatal — summary card just stays hidden
    }
  }, [orderId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    paymentApi.getMethods()
      .then(({ data }) => setSavedMethods(data))
      .catch(() => {})
      .finally(() => setFetchingMethods(false));
  }, []);

  // Auto-fill cardholder name from saved method if selected
  useEffect(() => {
    if (selectedMethod !== 'new') {
      const saved = savedMethods.find(m => String(m.saved_method_id) === selectedMethod);
      if (saved) setCardholderName(saved.cardholder_name);
    }
  }, [selectedMethod, savedMethods]);

  const handlePay = async () => {
    setLoading(true); setError(null);
    try {
      let payResult;
      if (selectedMethod !== 'new') {
        payResult = await paymentApi.payWithSaved(orderId, selectedMethod);
      } else {
        payResult = await paymentApi.processPayment(orderId, {
          card_number:     cardNumber.replace(/\s/g, ''),
          expiry_date:     expiryDate, // correct field name
          cvv:             cvv,
          cardholder_name: cardholderName, // required field
        });
      }
      // Backend returns PaymentStatus "Accepted" or "Declined" (never throws for declined)
      if (payResult?.data?.status === 'Declined') {
        setError('Your payment was declined. Please check your card details and try again.');
        return;
      }
      const { data } = await paymentApi.getReceipt(orderId);
      setReceipt(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Payment failed. Please try again.');
    } finally { setLoading(false); }
  };

  // Receipt / Success Screen
  if (receipt) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default',
        display: 'flex', alignItems: 'center', justifyContent: 'center', px: 2 }}>
        <Card sx={{ maxWidth: 480, width: '100%' }}>
          <CardContent sx={{ py: 5, px: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <CheckCircleOutlineIcon sx={{ fontSize: 64, color: '#C0392B', mb: 2 }} />
              <Typography variant="h2" sx={{ fontSize: '1.6rem', color: '#1C2833', mb: 0.5 }}>
                Order Confirmed!
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {receipt.message}
              </Typography>
            </Box>
            <Divider sx={{ mb: 2.5, borderColor: '#EDE5D8' }} />
            {/* Receipt details */}
            <Stack spacing={1.5}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">Order ID</Typography>
                <Typography variant="body2" fontWeight={600}>{receipt.order_id}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">Card</Typography>
                <Typography variant="body2">•••• {receipt.last4}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">Cardholder</Typography>
                <Typography variant="body2">{receipt.cardholder_name}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">Date</Typography>
                <Typography variant="body2">
                  {new Date(receipt.timestamp).toLocaleString()}
                </Typography>
              </Box>
              <Divider sx={{ borderColor: '#EDE5D8' }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1" fontWeight={700}>Total Paid</Typography>
                <Typography variant="body1" fontWeight={700} color="primary">
                  {/* receipt.amount is a Decimal string from backend */}
                  ${parseFloat(receipt.amount).toFixed(2)}
                </Typography>
              </Box>
            </Stack>
            <Divider sx={{ my: 3, borderColor: '#EDE5D8' }} />
            <Button variant="contained" color="primary" fullWidth
              onClick={() => navigate('/restaurants')}>
              Back to Restaurants
            </Button>
          </CardContent>
        </Card>
      </Box>
    );
  }

  // Payment Form
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', px: { xs: 2, sm: 4 }, py: 5 }}>
      <Box sx={{ maxWidth: 560, mx: 'auto' }}>
        <Typography variant="h2" sx={{ mb: 1, fontSize: '2rem', color: '#1C2833' }}>
          Payment
        </Typography>
        <Box sx={{ height: 4, width: 48,
          background: 'linear-gradient(90deg, #C0392B, #E74C3C)',
          borderRadius: 2, mb: 4 }} />
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        {/* Order total from checkout */}
        {order && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h4" sx={{ mb: 1.5, fontSize: '1rem', fontWeight: 600 }}>
                Order Summary
              </Typography>
              <Stack spacing={0.75}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Subtotal</Typography>
                  <Typography variant="body2">${parseFloat(order.subtotal).toFixed(2)}</Typography>
                </Box>
                {parseFloat(order.discount) > 0 && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="success.main">
                      Discount {order.coupon_code ? `(${order.coupon_code})` : ''}
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      -${parseFloat(order.discount).toFixed(2)}
                    </Typography>
                  </Box>
                )}
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Tax</Typography>
                  <Typography variant="body2">${parseFloat(order.tax).toFixed(2)}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Delivery fee</Typography>
                  <Typography variant="body2">${parseFloat(order.delivery_fee).toFixed(2)}</Typography>
                </Box>
                <Divider sx={{ borderColor: '#EDE5D8' }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body1" fontWeight={700}>Total</Typography>
                  <Typography variant="body1" fontWeight={700} color="primary">
                    ${parseFloat(order.total).toFixed(2)}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        )}
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
                  <FormControlLabel key={m.saved_method_id}
                    value={String(m.saved_method_id)}
                    control={<Radio color="primary" />}
                    label={
                      <Typography variant="body2">
                        •••• {m.last4} — {m.cardholder_name}
                        {m.nickname ? ` (${m.nickname})` : ''}
                        <Typography component="span" variant="caption"
                          color="text.secondary"> exp {m.expiry_date}</Typography>
                      </Typography>
                    }
                  />
                ))}
                <FormControlLabel value="new" control={<Radio color="primary" />}
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
                <TextField fullWidth size="small" label="Cardholder Name"
                  placeholder="John Smith"
                  value={cardholderName}
                  onChange={(e) => setCardholderName(e.target.value)} />
                <TextField fullWidth size="small" label="Card Number"
                  placeholder="1234 5678 9012 3456"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value)}
                  inputProps={{ maxLength: 19 }} />
                <Stack direction="row" spacing={2}>
                  <TextField fullWidth size="small" label="Expiry (MM/YY)"
                    placeholder="MM/YY"
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(e.target.value)} />
                  <TextField fullWidth size="small" label="CVV"
                    placeholder="123"
                    value={cvv}
                    onChange={(e) => setCvv(e.target.value)}
                    inputProps={{ maxLength: 4 }} />
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        )}
        <Button variant="contained" color="primary" fullWidth size="large"
          disabled={loading} onClick={handlePay}>
          {loading
            ? <CircularProgress size={22} color="inherit" />
            : `Pay Now${order ? ` · $${parseFloat(order.total).toFixed(2)}` : ''}`
          }
        </Button>
      </Box>
    </Box>
  );
}
