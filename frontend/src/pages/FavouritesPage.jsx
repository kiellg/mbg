import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Typography, CircularProgress, Alert,
    Stack, Card, CardContent, CardActionArea,
    IconButton, Tooltip, Chip, Divider, Tabs, Tab,
} from '@mui/material';
import { Favorite, Restaurant, MenuBook, Star, LocationOn, AccessTime } from '@mui/icons-material';
import DashboardLayout from '../components/shared/DashboardLayout';
import { favouritesApi } from '../api/favourites';
import { restaurantApi } from '../api/restaurant';


export default function FavouritesPage() {
    const navigate = useNavigate();
    const [favourites, setFavourites] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [tab, setTab] = useState(0);

    useEffect(() => {
        favouritesApi.getAll()
            .then(async (res) => {
                const raw = res.data;

                // Collect unique restaurant IDs needed across both types
                const restaurantIds = [
                    ...new Set([
                        ...raw
                            .filter(f => f.target_type === 'restaurant')
                            .map(f => String(f.target_id)),
                        ...raw
                            .filter(f => f.target_type === 'menu_item' && f.restaurant_id != null)
                            .map(f => String(f.restaurant_id)),
                    ])
                ];

                // Fetch all needed menus in parallel
                const restaurantMap = {};
                await Promise.all(
                    restaurantIds.map(rid =>
                        restaurantApi.getMenu(rid)
                            .then(r => { restaurantMap[rid] = r.data; })
                            .catch(() => {})
                    )
                );

                // Enrich each favourite with details from the fetched menus
                const enriched = raw.map(fav => {
                    if (fav.target_type === 'restaurant') {
                        const r = restaurantMap[String(fav.target_id)];
                        return r
                            ? { ...fav, name: r.name, address: r.address, rating: r.rating,
                                cuisine_type: r.cuisine_type, opening_hours: r.opening_hours }
                            : fav;
                    }
                    if (fav.target_type === 'menu_item') {
                        const r = restaurantMap[String(fav.restaurant_id)];
                        const item = r?.menu?.find(i => String(i.id) === String(fav.target_id));
                        return item
                            ? { ...fav, name: item.name, description: item.description,
                                price_cents: item.price_cents, dietary_tag: item.dietary_tag,
                                restaurant_name: r.name }
                            : fav;
                    }
                    return fav;
                });

                setFavourites(enriched);
            })
            .catch((err) => setError(err.response?.data?.detail || 'Failed to load favourites'))
            .finally(() => setLoading(false));
    }, []);

    const handleRemove = async (targetId, targetType, restaurantId = null) => {
        await favouritesApi.remove(String(targetId), targetType, restaurantId);
        setFavourites((prev) =>
            prev.filter((f) => !(
                String(f.target_id) === String(targetId) &&
                f.target_type === targetType &&
                (targetType !== 'menu_item' || String(f.restaurant_id) === String(restaurantId))
            ))
        );
    };

    const restaurants = favourites.filter((f) => f.target_type === 'restaurant');
    const menuItems   = favourites.filter((f) => f.target_type === 'menu_item');
    const displayed   = tab === 0 ? restaurants : menuItems;

    return (
        <DashboardLayout>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 0.5 }}>Favourites</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Your saved restaurants and menu items
            </Typography>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <>
                    <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
                        <Tab icon={<Restaurant fontSize="small" />} iconPosition="start"
                            label={`Restaurants (${restaurants.length})`} />
                        <Tab icon={<MenuBook fontSize="small" />} iconPosition="start"
                            label={`Menu Items (${menuItems.length})`} />
                    </Tabs>
                    <Divider sx={{ mb: 3 }} />
                    {displayed.length === 0 ? (
                        <Box sx={{ textAlign: 'center', py: 8 }}>
                            <Favorite sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                            <Typography color="text.secondary">
                                {tab === 0
                                    ? 'No favourite restaurants yet. Browse restaurants and tap the heart.'
                                    : 'No favourite menu items yet. Open a restaurant and tap the heart on an item.'}
                            </Typography>
                        </Box>
                    ) : (
                        <Stack spacing={1.5}>
                            {displayed.map((fav) => (
                                <FavouriteCard
                                    key={`${fav.target_type}-${fav.restaurant_id ?? fav.target_id}-${fav.target_id}`}
                                    fav={fav}
                                    onRemove={handleRemove}
                                    onNavigate={() => navigate(
                                        fav.target_type === 'restaurant'
                                            ? `/restaurants/${fav.target_id}`
                                            : `/restaurants/${fav.restaurant_id}`
                                    )}
                                />
                            ))}
                        </Stack>
                    )}
                </>
            )}
        </DashboardLayout>
    );
}


function FavouriteCard({ fav, onRemove, onNavigate }) {
    return (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CardActionArea onClick={onNavigate} sx={{ flex: 1 }}>
                    <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>

                        {/* Name row */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Chip size="small"
                                label={fav.target_type === 'restaurant' ? 'Restaurant' : 'Menu item'}
                                color={fav.target_type === 'restaurant' ? 'primary' : 'default'}
                                variant="outlined" sx={{ fontSize: '0.65rem', height: 20 }} />
                            <Typography variant="body1" fontWeight={600} sx={{ fontSize: '0.95rem' }}>
                                {fav.name ?? `ID: ${fav.target_id}`}
                            </Typography>
                        </Box>

                        {/* Restaurant details */}
                        {fav.target_type === 'restaurant' && (
                            <Stack direction="row" spacing={1.5} flexWrap="wrap" sx={{ mt: 0.5 }}>
                                {fav.rating && (
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        <Star sx={{ fontSize: 13, color: '#f59e0b' }} />
                                        <Typography variant="caption" color="text.secondary">
                                            {fav.rating} / 5
                                        </Typography>
                                    </Box>
                                )}
                                {fav.opening_hours && (
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        <AccessTime sx={{ fontSize: 13, color: 'text.secondary' }} />
                                        <Typography variant="caption" color="text.secondary">
                                            {fav.opening_hours}
                                        </Typography>
                                    </Box>
                                )}
                                {fav.address && (
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        <LocationOn sx={{ fontSize: 13, color: 'text.secondary' }} />
                                        <Typography variant="caption" color="text.secondary">
                                            {fav.address}
                                        </Typography>
                                    </Box>
                                )}
                                {fav.cuisine_type && (
                                    <Chip label={fav.cuisine_type} size="small"
                                        sx={{ height: 18, fontSize: '0.65rem' }} />
                                )}
                            </Stack>
                        )}

                        {/* Menu item details */}
                        {fav.target_type === 'menu_item' && (
                            <Stack spacing={0.25} sx={{ mt: 0.25 }}>
                                {fav.restaurant_name && (
                                    <Typography variant="caption" color="text.secondary">
                                        from {fav.restaurant_name}
                                    </Typography>
                                )}
                                {fav.description && (
                                    <Typography variant="caption" color="text.secondary"
                                        sx={{ overflow: 'hidden', textOverflow: 'ellipsis',
                                              display: '-webkit-box', WebkitLineClamp: 2,
                                              WebkitBoxOrient: 'vertical' }}>
                                        {fav.description}
                                    </Typography>
                                )}
                                <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.25 }}>
                                    {fav.price_cents != null && (
                                        <Typography variant="caption" fontWeight={600}>
                                            ${(fav.price_cents / 100).toFixed(2)}
                                        </Typography>
                                    )}
                                    {fav.dietary_tag && (
                                        <Chip label={fav.dietary_tag} size="small"
                                            sx={{ height: 18, fontSize: '0.65rem' }} />
                                    )}
                                </Stack>
                            </Stack>
                        )}

                    </CardContent>
                </CardActionArea>
                <Tooltip title="Remove from favourites">
                    <IconButton size="small" sx={{ mr: 1.5 }}
                        onClick={() => onRemove(fav.target_id, fav.target_type, fav.restaurant_id)}>
                        <Favorite fontSize="small" sx={{ color: 'error.main' }} />
                    </IconButton>
                </Tooltip>
            </Box>
        </Card>
    );
}