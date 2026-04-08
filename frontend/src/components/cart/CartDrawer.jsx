import {
  Drawer, Box, Typography, IconButton,
  Divider, Button, CircularProgress, Alert
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import CartItem from './CartItem';

export default function CartDrawer({ open, onClose, restaurantId }) {
  const navigate = useNavigate();
  const { cart, loading, error } = useCart();

  const cartBelongsHere = cart?.restaurant_id === Number(restaurantId);
  const items = cartBelongsHere ? (cart?.items ?? []) : [];
  const isEmpty = items.length === 0;

  return (
    <Drawer anchor="right" open={open} onClose={onClose}
      PaperProps={{ sx: { width: { xs: '100%', sm: 400 },
        display: 'flex', flexDirection: 'column' } }}>

      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        px: 2.5, py: 2, borderBottom: '1px solid #EDE5D8' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ShoppingCartIcon color="primary" />
          <Typography variant="h6" fontWeight={700}>Your Cart</Typography>
          {!isEmpty && (
            <Typography variant="body2" color="text.secondary">
              ({items.reduce((sum, i) => sum + i.quantity, 0)} items)
            </Typography>
          )}
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Scrollable body */}
      <Box sx={{ flex: 1, overflowY: 'auto', px: 2.5, py: 2 }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={28} sx={{ color: '#C0392B' }} />
          </Box>
        )}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {!loading && isEmpty && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <ShoppingCartIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography color="text.secondary" fontWeight={600}>Your cart is empty</Typography>
            <Typography variant="body2" color="text.secondary">
              Add items from the menu to get started.
            </Typography>
          </Box>
        )}
        {!loading && !isEmpty && items.map((item) => (
          <CartItem key={item.id} item={item} restaurantId={restaurantId} />
        ))}
      </Box>

      {/* Footer — total + checkout */}
      {!isEmpty && (
        <Box sx={{ px: 2.5, py: 2.5, borderTop: '1px solid #EDE5D8', bgcolor: '#FDFBF8' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="body1" fontWeight={700}>Total</Typography>
            <Typography variant="body1" fontWeight={700} color="primary">
              {cart?.display_cart_subtotal ?? '—'}
            </Typography>
          </Box>
          <Button variant="contained" color="primary" fullWidth size="large"
            onClick={() => { onClose(); navigate(`/checkout/${restaurantId}`); }}>
            Proceed to Checkout
          </Button>
        </Box>
      )}
    </Drawer>
  );
}