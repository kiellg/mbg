import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
    Box, Typography, CircularProgress, Alert,
    Chip, Divider, Stack, IconButton, Tooltip,
} from '@mui/material';
import { Star, AccessTime, LocationOn, Favorite, FavoriteBorder } from '@mui/icons-material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { restaurantApi } from '../../api/restaurant';
import { favouritesApi } from '../../api/favourites';
import MenuItemCard from '../../components/restaurant/MenuItemCard';


export default function RestaurantDetailPage() {
    const { id } = useParams();
    const [restaurant, setRestaurant] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [favourites, setFavourites] = useState(new Set());


    useEffect(() => {
        Promise.all([
            restaurantApi.getMenu(id),
            favouritesApi.getAll().catch(() => ({ data: [] })),
        ]).then(([rRes, fRes]) => {
            setRestaurant(rRes.data);
            setFavourites(new Set(fRes.data.map((f) =>
                f.target_type === 'menu_item'
                    ? `menu_item:${String(f.restaurant_id)}:${String(f.target_id)}`
                    : `restaurant:${String(f.target_id)}`
            )));
        })
        .catch((err) => setError(err.response?.data?.detail || 'Failed to load restaurant'))
        .finally(() => setLoading(false));
    }, [id]);


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
        } catch (_) {}
    };


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
                {restaurant.rating && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Star sx={{ fontSize: 16, color: '#f59e0b' }} />
                        <Typography variant="body2" fontWeight={600}>{restaurant.rating} / 5</Typography>
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
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Menu</Typography>
            {visibleItems.length === 0 ? (
                <Typography color="text.secondary">No menu items available.</Typography>
            ) : (
                <Stack spacing={1.5}>
                    {visibleItems.map((item) => (
                        <Box key={item.id} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ flex: 1 }}>
                                <MenuItemCard item={item} />
                            </Box>
                            {/* ✅ key now includes restaurant.id so item:1 in restaurant A ≠ item:1 in restaurant B */}
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
        </DashboardLayout>
    );
}