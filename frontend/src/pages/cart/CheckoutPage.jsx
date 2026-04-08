import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, RadioGroup,
  FormControlLabel, Radio, TextField, Button,
  Alert, CircularProgress, Divider, Stack,
  Switch, Collapse
} from '@mui/material';
import ScheduleIcon from '@mui/icons-material/Schedule';
import DirectionsWalkIcon from '@mui/icons-material/DirectionsWalk';
import DirectionsBikeIcon from '@mui/icons-material/DirectionsBike';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useCart } from '../../context/CartContext';
import { checkoutApi } from '../../api/checkout';

const DELIVERY_OPTIONS = [
  { value: 'walk', label: 'Walk', icon: <DirectionsWalkIcon fontSize="small" /> },
  { value: 'bike', label: 'Bike', icon: <DirectionsBikeIcon fontSize="small" /> },
  { value: 'car',  label: 'Car',  icon: <DirectionsCarIcon fontSize="small" /> },
];

// Minimum scheduled time = 15 minutes from now
function getMinScheduledTime() {
  const d = new Date(Date.now() + 15 * 60 * 1000);
  // datetime-local input needs format: YYYY-MM-DDTHH:MM
  return d.toISOString().slice(0, 16);
}

export default function CheckoutPage() {
  const { restaurantId } = useParams();
  const navigate = useNavigate();
  const { cart, clearCart } = useCart();

  const [deliveryMethod, setDeliveryMethod] = useState('walk');
  const [couponCode, setCouponCode]         = useState('');
  const [isScheduled, setIsScheduled]       = useState(false);
  const [scheduledTime, setScheduledTime]   = useState('');
  const [loading, setLoading]               = useState(false);
  const [error, setError]                   = useState(null);

  const subtotal = cart?.display_cart_subtotal ?? '—';

  const handleCheckout = async () => {
    if (isScheduled && !scheduledTime) {
      setError('Please select a scheduled time.');
      return;
    }
    setLoading(true); setError(null);
    try {
      const { data } = await checkoutApi.checkout(restaurantId, {
        delivery_method: deliveryMethod,
        ...(couponCode && { coupon_code: couponCode }),
        is_scheduled: isScheduled,
        ...(isScheduled && { scheduled_time: new Date(scheduledTime).toISOString() }),
      });
      clearCart();
      navigate(`/payment/${data.order_id}`, { state: { order: data } });
    } catch (err) {
      const detail = err.response?.data?.detail || 'Checkout failed. Please try again.';
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally { setLoading(false); }
  };

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
            <RadioGroup value={deliveryMethod}
              onChange={(e) => setDeliveryMethod(e.target.value)}>
              {DELIVERY_OPTIONS.map(({ value, label, icon }) => (
                <FormControlLabel key={value} value={value}
                  control={<Radio color="primary" />}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {icon}
                      <Typography variant="body2">{label}</Typography>
                    </Box>
                  }
                />
              ))}
            </RadioGroup>

            <Divider sx={{ my: 2.5, borderColor: '#EDE5D8' }} />

            {/* Coupon */}
            <Typography variant="h4" sx={{ mb: 1.5, fontSize: '1rem', fontWeight: 600 }}>
              Coupon Code{' '}
              <Typography component="span" variant="body2" color="text.secondary">(optional)</Typography>
            </Typography>
            <TextField fullWidth size="small" placeholder="Enter coupon code"
              value={couponCode}
              onChange={(e) => setCouponCode(e.target.value)} />

            <Divider sx={{ my: 2.5, borderColor: '#EDE5D8' }} />

            {/* Schedule Toggle */}
            <Box sx={{ display: 'flex', alignItems: 'center',
              justifyContent: 'space-between', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ScheduleIcon fontSize="small" color={isScheduled ? 'primary' : 'disabled'} />
                <Typography variant="body2" fontWeight={600}>
                  Schedule for later
                </Typography>
              </Box>
              <Switch
                checked={isScheduled}
                onChange={(e) => {
                  setIsScheduled(e.target.checked);
                  if (!e.target.checked) setScheduledTime('');
                }}
                color="primary"
              />
            </Box>

            <Collapse in={isScheduled}>
              <TextField
                fullWidth
                size="small"
                type="datetime-local"
                label="Scheduled time"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                inputProps={{ min: getMinScheduledTime() }}
                InputLabelProps={{ shrink: true }}
                sx={{ mt: 1 }}
                helperText="Minimum 15 minutes from now"
              />
            </Collapse>
          </CardContent>
        </Card>

        {/* Order Summary */}
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
              {isScheduled && scheduledTime && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Scheduled for</Typography>
                  <Typography variant="body2" color="primary" fontWeight={600}>
                    {new Date(scheduledTime).toLocaleString()}
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
          {loading
            ? <CircularProgress size={22} color="inherit" />
            : isScheduled ? 'Schedule Order' : 'Place Order'}
        </Button>

      </Box>
    </Box>
  );
}