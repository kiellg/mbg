import { Box, Typography, Button, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export default function CartSummary({ cart, restaurantId }) {
  const navigate = useNavigate();
  const total = cart?.total ?? 0;

  return (
    <Box sx={{ mt: 3, p: 3, bgcolor: '#FDFBF8',
      borderRadius: 3, border: '1px solid #EDE5D8' }}>
      <Typography variant="h4" sx={{ mb: 2, fontSize: '1.1rem' }}>
        Order Summary
      </Typography>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">Subtotal</Typography>
        <Typography variant="body2">${total.toFixed(2)}</Typography>
      </Box>

      <Divider sx={{ my: 1.5, borderColor: '#EDE5D8' }} />

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2.5 }}>
        <Typography variant="body1" fontWeight={700}>Total</Typography>
        <Typography variant="body1" fontWeight={700} color="primary">
          ${total.toFixed(2)}
        </Typography>
      </Box>

      <Button variant="contained" color="primary" fullWidth
        onClick={() => navigate(`/checkout/${restaurantId}`)}>
        Proceed to Checkout
      </Button>
    </Box>
  );
}