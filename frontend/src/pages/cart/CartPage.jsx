import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Alert, CircularProgress, Card, CardContent } from '@mui/material';
import ShoppingCartOutlinedIcon from '@mui/icons-material/ShoppingCartOutlined';
import { useCart } from '../../context/CartContext';
import CartItem from '../../components/cart/CartItem';
import CartSummary from '../../components/cart/CartSummary';

export default function CartPage() {
  const { restaurantId } = useParams();
  const { cart, loading, error, fetchCart } = useCart();

  useEffect(() => { fetchCart(restaurantId); }, [restaurantId]);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', px: { xs: 2, sm: 4 }, py: 5 }}>
      <Box sx={{ maxWidth: 680, mx: 'auto' }}>

        {/* Header */}
        <Typography variant="h2" sx={{ mb: 1, fontSize: '2rem', color: '#1C2833' }}>
          Your Cart
        </Typography>
        <Box sx={{ height: 4, width: 48,
          background: 'linear-gradient(90deg, #C0392B, #E74C3C)',
          borderRadius: 2, mb: 4 }} />

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {loading && !cart && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress sx={{ color: '#C0392B' }} />
          </Box>
        )}

        {/* Empty state */}
        {!loading && cart?.items?.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 10, color: '#5D6D7E' }}>
            <ShoppingCartOutlinedIcon sx={{ fontSize: 64, mb: 2, opacity: 0.4 }} />
            <Typography variant="h4" sx={{ fontSize: '1.2rem', mb: 1 }}>
              Your cart is empty
            </Typography>
            <Typography variant="body2">
              Add items from a restaurant to get started.
            </Typography>
          </Box>
        )}

        {/* Cart items */}
        {cart?.items?.length > 0 && (
          <Card>
            <CardContent sx={{ px: 3, pt: 2.5, pb: '16px !important' }}>
              {cart.items.map(item => (
                <CartItem key={item.item_id} item={item} restaurantId={restaurantId} />
              ))}
            </CardContent>
          </Card>
        )}

        {cart?.items?.length > 0 && (
          <CartSummary cart={cart} restaurantId={restaurantId} />
        )}

      </Box>
    </Box>
  );
}