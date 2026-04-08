import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, RadioGroup,
  FormControlLabel, Radio, TextField, Button,
  Alert, CircularProgress, Divider, Chip, Stack
} from '@mui/material';
import DirectionsWalkIcon from '@mui/icons-material/DirectionsWalk';
import DirectionsBikeIcon from '@mui/icons-material/DirectionsBike';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useCart } from '../../context/CartContext';
import { checkoutApi } from '../../api/checkout';

const DELIVERY_OPTIONS = [
  { value: 'walk', label: 'Walk',  icon: <DirectionsWalkIcon fontSize="small" /> },
  { value: 'bike', label: 'Bike',  icon: <DirectionsBikeIcon fontSize="small" /> },
  { value: 'car',  label: 'Car',   icon: <DirectionsCarIcon fontSize="small" /> },
];

// Delivery fees must match backend logic
const DELIVERY_FEE_LABELS = {
  walk: '$5.00',
  bike: '$8.00',
  car:  '$10.00',
};

export default function CheckoutPage() {
  const { restaurantId } = useParams();
  const navigate = useNavigate();
  const { cart, clearCart } = useCart();

  const [deliveryMethod, setDeliveryMethod] = useState('walk');
  const [couponCode, setCouponCode]         = useState('');
  const [couponApplied, setCouponApplied]   = useState(false);
  const [order, setOrder]                   = useState(null); // holds OrderResponse after checkout
  const [loading, setLoading]               = useState(false);
  const [error, setError]                   = useState(null);

  const handleCheckout = async () => {
    setLoading(true); setError(null);
    try {
      const { data } = await checkoutApi.checkout(restaurantId, {
        delivery_method: deliveryMethod,
        ...(couponCode && { coupon_code: couponCode }),
                    });
      // If a coupon was submitted, mark it as applied on success
      if (couponCode) setCouponApplied(true);
      clearCart();
      // data is OrderResponse — navigate with order embedded in state
      navigate(`/payment/${data.order_id}`, { state: { order: data } });
    } catch (err) {
      const detail = err.response?.data?.detail || 'Checkout failed. Please try again.';
      // If coupon-specific error, show inline
      if (typeof detail === 'string' && detail.toLowerCase().includes('coupon')) {
        setError(`Coupon error: ${detail}`);
        setCouponApplied(false);
      } else {
        setError(detail);
      }
    } finally { setLoading(false); }
  };

  const subtotal = cart?.display_cart_subtotal ?? '—';

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', px: { xs: 2, sm: 4 }, py: 5 }}>
      <Box sx={{ maxWidth: 600, mx: 'auto' }}>

        <Typography variant="h2" sx={{ mb: 1, fontSize: '2rem', color: '#1C2833' }}>
          Checkout
        </Typography>
        <Box sx={{ height: 4, width: 48,
          background: 'linear-gradient(90deg, #C0392B, #E74C3C)',
          borderRadius: 2, mb: 4 }} />

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        {/* Delivery Method */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h4" sx={{ mb: 2, fontSize: '1rem', fontWeight: 600 }}>
              Delivery Method
            </Typography>
            <RadioGroup value={deliveryMethod} onChange={(e) => setDeliveryMethod(e.target.value)}>
              {DELIVERY_OPTIONS.map(({ value, label, icon }) => (
                <FormControlLabel key={value} value={value}
                  control={<Radio color="primary" />}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      width: '100%', gap: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {icon}
                        <Typography variant="body2">{label}</Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        +{DELIVERY_FEE_LABELS[value]}
                      </Typography>
                    </Box>
                  }
                  sx={{ width: '100%', mr: 0 }}
                />
              ))}
            </RadioGroup>

            <Divider sx={{ my: 2.5, borderColor: '#EDE5D8' }} />

            {/* Coupon */}
            <Typography variant="h4" sx={{ mb: 1.5, fontSize: '1rem', fontWeight: 600 }}>
              Coupon Code{' '}
              <Typography component="span" variant="body2" color="text.secondary">(optional)</Typography>
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <TextField fullWidth size="small" placeholder="Enter coupon code"
                value={couponCode}
                onChange={(e) => { setCouponCode(e.target.value); setCouponApplied(false); }}
                disabled={couponApplied}
              />
              {couponApplied && (
                <Chip icon={<CheckCircleIcon />} label="Applied" color="success" size="small" />
              )}
            </Stack>
            {couponCode && !couponApplied && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                Coupon will be applied when you place the order.
              </Typography>
            )}
          </CardContent>
        </Card>

        {/* Cost Breakdown */}
        <Card sx={{ mb: 3 }}>
            <CardContent>
                <Typography variant="h4" sx={{ mb: 2, fontSize: '1rem', fontWeight: 600 }}>
                    Order Summary
                </Typography>
                <Stack spacing={1}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">Items subtotal</Typography>
                        <Typography variant="body2">{subtotal}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">Delivery fee</Typography>
                        <Typography variant="body2" color="text.secondary" fontStyle="italic">
                            Calculated at order placement
                        </Typography>
                    </Box>
                    {couponCode && (
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="success.main">
                                Coupon ({couponCode})
                            </Typography>
                            <Typography variant="body2" color="success.main">
                                Applied at order placement
                            </Typography>
                        </Box>
                    )}
                </Stack>
                <Divider sx={{ my: 1.5, borderColor: '#EDE5D8' }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body1" fontWeight={700}>Estimated Total</Typography>
                    <Typography variant="body1" fontWeight={700} color="primary">{subtotal}</Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                    * Final breakdown with tax, delivery fee, and discounts shown on the next screen
                </Typography>
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
