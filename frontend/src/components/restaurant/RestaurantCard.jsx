import { Card, CardContent, CardActionArea, Box, Typography, Chip } from '@mui/material';
import { Star, AccessTime } from '@mui/icons-material';

export default function RestaurantCard({ restaurant, onClick }) {
    return (
        <Card sx={{ height: '100%', borderRadius: 3, border: '1px solid', borderColor: 'divider' }} elevation={0}>
            <CardActionArea onClick={onClick} sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="h6" fontWeight={600} sx={{ fontSize: '1rem', lineHeight: 1.3 }}>
                            {restaurant.name}
                        </Typography>
                        {restaurant.rating && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 1, flexShrink: 0 }}>
                                <Star sx={{ fontSize: 14, color: '#f59e0b' }} />
                                <Typography variant="body2" fontWeight={600}>{restaurant.rating}</Typography>
                            </Box>
                        )}
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, fontSize: '0.8rem' }}>
                        {restaurant.address}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {restaurant.cuisine_type && (
                            <Chip label={restaurant.cuisine_type} size="small" sx={{ fontSize: '0.7rem', height: 22 }} />
                        )}
                        {restaurant.opening_hours && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <AccessTime sx={{ fontSize: 12, color: 'text.secondary' }} />
                                <Typography variant="caption" color="text.secondary">{restaurant.opening_hours}</Typography>
                            </Box>
                        )}
                    </Box>
                </CardContent>
            </CardActionArea>
        </Card>
    );
}