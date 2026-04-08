// src/pages/checkout/CheckoutPage.jsx
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, RadioGroup,
  FormControlLabel, Radio, TextField, Button,
  Alert, CircularProgress, Divider
} from '@mui/material';
import { useCart } from '../../context/CartContext';
import { checkoutApi } from '../../api/checkout';

export default function CheckoutPage() {
  const { restaurantId } = useParams();
  const navigate = useNavigate();
  const { cart } = useCart();

  const [deliveryMethod, setDeliveryMethod] = useState('delivery');
  const [couponCode, setCouponCode]         = useState('');
  const [loading, setLoading]               = useState(false);
  const [error, setError]                   = useState(null);

  const handleCheckout = async () => {
    setLoading(true); setError(null);
    try {
      const { data } = await checkoutApi.checkout(restaurantId, {
        delivery_method: deliveryMethod,
        ...(couponCode && { coupon_code: couponCode }),
      });
      // data should return the order_id → hand off to Payment
      // navigate(`/payment/${data.order_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Checkout failed. Please try again.');
    } finally { setLoading(false); }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', px: { xs: 2, sm: 4 }, py: 5 }}>
      <Box sx={{ maxWidth: 600, mx: 'auto' }}>

        {/* Header */}
        <Typography variant="h2" sx={{ mb: 1, fontSize: '2rem', color: '#1C2833' }}>
          Checkout
        </Typography>
        <Box sx={{ height: 4, width: 48,
          background: 'linear-gradient(90deg, #C0392B, #E74C3C)',
          borderRadius: 2, mb: 4 }} />

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        <Card sx={{ mb: 3 }}>
          <CardContent>
            {/* Delivery method */}
            <Typography variant="h4" sx={{ mb: 2, fontSize: '1rem', fontWeight: 600 }}>
              Delivery Method
            </Typography>
            <RadioGroup value={deliveryMethod} onChange={(e) => setDeliveryMethod(e.target.value)}>
              <FormControlLabel value="delivery" control={<Radio color="primary" />} label="Delivery" />
              <FormControlLabel value="pickup"   control={<Radio color="primary" />} label="Pickup" />
            </RadioGroup>

            <Divider sx={{ my: 2.5, borderColor: '#EDE5D8' }} />

            {/* Coupon */}
            <Typography variant="h4" sx={{ mb: 1.5, fontSize: '1rem', fontWeight: 600 }}>
              Coupon Code <Typography component="span" variant="body2" color="text.secondary">(optional)</Typography>
            </Typography>
            <TextField
              fullWidth size="small" placeholder="Enter coupon code"
              value={couponCode} onChange={(e) => setCouponCode(e.target.value)}
            />
          </CardContent>
        </Card>

        {/* Order total summary */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body1" fontWeight={700}>Order Total</Typography>
              <Typography variant="body1" fontWeight={700} color="primary">
                ${cart?.display_cart_subtotal ?? '—'}
              </Typography>
            </Box>
          </CardContent>
        </Card>

        <Button variant="contained" color="primary" fullWidth size="large"
          disabled={loading} onClick={handleCheckout}>
          {loading ? <CircularProgress size={22} color="inherit" /> : 'Place Order'}
        </Button>

      </Box>
    </Box>
  );
}