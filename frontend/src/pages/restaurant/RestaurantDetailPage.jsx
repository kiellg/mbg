import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, CircularProgress, Alert,
  Chip, Divider, Stack, IconButton, Tooltip,
  Badge, Fab, Snackbar, Card, CardContent,
} from '@mui/material';
import { Star, StarBorder, AccessTime, LocationOn, Favorite, FavoriteBorder } from '@mui/icons-material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { restaurantApi } from '../../api/restaurant';
import { favouritesApi } from '../../api/favourites';
import { reviewsApi } from '../../api/reviews';
import MenuItemCard from '../../components/restaurant/MenuItemCard';
import CartDrawer from '../../components/cart/CartDrawer';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';

// Renders filled/empty stars for a given rating out of 5
function StarRating({ rating }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25 }}>
      {[1, 2, 3, 4, 5].map((n) =>
        n <= rating
          ? <Star key={n} sx={{ fontSize: 16, color: '#f59e0b' }} />
          : <StarBorder key={n} sx={{ fontSize: 16, color: '#f59e0b' }} />
      )}
    </Box>
  );
}

export default function RestaurantDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { cart, addItem, fetchCart } = useCart();

  const [restaurant, setRestaurant]   = useState(null);
  const [reviews, setReviews]         = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);
  const [favourites, setFavourites]   = useState(new Set());
  const [cartOpen, setCartOpen]       = useState(false);
  const [snackbar, setSnackbar]       = useState({ open: false, message: '', severity: 'success' });

  const isCustomer = user?.role === 'customer';

  // Load restaurant + favourites + reviews together
  useEffect(() => {
    Promise.all([
      restaurantApi.getMenu(id),
      favouritesApi.getAll().catch(() => ({ data: [] })),
      reviewsApi.getForRestaurant(id).catch(() => ({ data: [] })),
    ])
      .then(([rRes, fRes, revRes]) => {
        setRestaurant(rRes.data);
        setFavourites(new Set(fRes.data.map((f) =>
          f.target_type === 'menu_item'
            ? `menu_item:${String(f.restaurant_id)}:${String(f.target_id)}`
            : `restaurant:${String(f.target_id)}`
        )));
        // Sort newest first
        const sorted = [...revRes.data].sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );
        setReviews(sorted);
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load restaurant'))
      .finally(() => setLoading(false));
  }, [id]);

  // Fetch cart on load — customers only
  useEffect(() => {
    if (isCustomer && id) fetchCart(id);
  }, [isCustomer, id, fetchCart]);

  // Add to cart handler
  const handleAddToCart = useCallback(async (item) => {
    const result = await addItem(id, { menu_item_id: item.id, quantity: 1 });
    if (result.success) {
      setSnackbar({ open: true, message: `${item.name} added to cart!`, severity: 'success' });
    } else {
      setSnackbar({ open: true, message: result.message || 'Failed to add item', severity: 'error' });
    }
  }, [id, addItem]);

  // Favourites toggle — original logic untouched
  const toggleFavourite = async (targetId, targetType, restaurantId = null) => {
    const key = targetType === 'menu_item'
      ? `menu_item:${String(restaurantId)}:${String(targetId)}`
      : `restaurant:${String(targetId)}`;
    try {
      if (favourites.has(key)) {
        await favouritesApi.remove(String(targetId), targetType, restaurantId);
        setFavourites((prev) => { const s = new Set(prev); s.delete(key); return s; });
      } else {
        await favouritesApi.add(String(targetId), targetType, restaurantId);
        setFavourites((prev) => new Set(prev).add(key));
      }
    } catch (_) {
      setSnackbar({ open: true, message: 'Could not update favourites. Try again.', severity: 'error' });
    }
  };

  const cartItemCount = cart?.items?.reduce((sum, i) => sum + i.quantity, 0) ?? 0;

  // Compute average rating from live review data
  const avgRating = reviews.length > 0
    ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
    : null;

  if (loading) return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
    </DashboardLayout>
  );

  if (error) return (
    <DashboardLayout>
      <Alert severity="error" sx={{ m: 3 }}>{error}</Alert>
    </DashboardLayout>
  );

  if (!restaurant) return null;

  const visibleItems = restaurant.menu?.filter((i) => i.is_visible && i.is_active) ?? [];

  return (
    <DashboardLayout>
      {/* Restaurant header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
        <Typography variant="h4" fontWeight={700}>{restaurant.name}</Typography>
        <Tooltip title={favourites.has(`restaurant:${String(restaurant.id)}`) ? 'Remove from favourites' : 'Save restaurant'}>
          <IconButton onClick={() => toggleFavourite(restaurant.id, 'restaurant')}>
            {favourites.has(`restaurant:${String(restaurant.id)}`)
              ? <Favorite sx={{ color: 'error.main' }} />
              : <FavoriteBorder />}
          </IconButton>
        </Tooltip>
      </Box>

      <Stack direction="row" spacing={2} flexWrap="wrap" sx={{ mb: 2 }}>
        {/* Use live avg rating from reviews if available, fall back to restaurant.rating */}
        {(avgRating || restaurant.rating) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Star sx={{ fontSize: 16, color: '#f59e0b' }} />
            <Typography variant="body2" fontWeight={600}>
              {avgRating ?? restaurant.rating} / 5
              {reviews.length > 0 && (
                <Typography component="span" variant="body2" color="text.secondary">
                  {' '}· {reviews.length} {reviews.length === 1 ? 'review' : 'reviews'}
                </Typography>
              )}
            </Typography>
          </Box>
        )}
        {restaurant.opening_hours && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <AccessTime sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">{restaurant.opening_hours}</Typography>
          </Box>
        )}
        {restaurant.address && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <LocationOn sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">{restaurant.address}</Typography>
          </Box>
        )}
        {restaurant.cuisine_type && <Chip label={restaurant.cuisine_type} size="small" />}
      </Stack>

      <Divider sx={{ mb: 3 }} />

      {/* Menu section — unchanged */}
      <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Menu</Typography>
      {visibleItems.length === 0 ? (
        <Typography color="text.secondary">No menu items available.</Typography>
      ) : (
        <Stack spacing={1.5}>
          {visibleItems.map((item) => (
            <Box key={item.id} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ flex: 1 }}>
                <MenuItemCard
                  item={item}
                  onClick={() => navigate(`/restaurants/${id}/menu/${item.id}`)}
                  onAddToCart={isCustomer ? handleAddToCart : undefined}
                />
              </Box>
              <Tooltip title={favourites.has(`menu_item:${String(restaurant.id)}:${String(item.id)}`) ? 'Remove from favourites' : 'Save item'}>
                <IconButton size="small"
                  onClick={() => toggleFavourite(item.id, 'menu_item', restaurant.id)}>
                  {favourites.has(`menu_item:${String(restaurant.id)}:${String(item.id)}`)
                    ? <Favorite fontSize="small" sx={{ color: 'error.main' }} />
                    : <FavoriteBorder fontSize="small" />}
                </IconButton>
              </Tooltip>
            </Box>
          ))}
        </Stack>
      )}

      {/* Reviews section */}
      <Divider sx={{ my: 4 }} />
      <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
        Customer Reviews
        {reviews.length > 0 && (
          <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            ({reviews.length})
          </Typography>
        )}
      </Typography>

      {reviews.length === 0 ? (
        <Typography color="text.secondary" variant="body2">
          No reviews yet — be the first to leave one after your order!
        </Typography>
      ) : (
        <Stack spacing={2} sx={{ mb: 10 }}>
          {reviews.map((review) => (
            <Card key={review.review_id} variant="outlined">
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <StarRating rating={review.rating} />
                  <Typography variant="caption" color="text.secondary">
                    {new Date(review.created_at).toLocaleDateString(undefined, {
                      year: 'numeric', month: 'short', day: 'numeric',
                    })}
                  </Typography>
                </Box>
                {review.comment && (
                  <Typography variant="body2" color="text.secondary">
                    {review.comment}
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}

      {/* Floating cart button + drawer — customers only */}
      {isCustomer && (
        <>
          <Fab color="primary" onClick={() => setCartOpen(true)}
            sx={{ position: 'fixed', bottom: 32, right: 32, zIndex: 1200 }}>
            <Badge badgeContent={cartItemCount} color="error" max={99}>
              <ShoppingCartIcon />
            </Badge>
          </Fab>
          <CartDrawer
            open={cartOpen}
            onClose={() => setCartOpen(false)}
            restaurantId={id}
          />
        </>
      )}

      {/* Add to cart snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={2500}
        onClose={() => setSnackbar(s => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity} variant="filled" sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </DashboardLayout>
  );
}