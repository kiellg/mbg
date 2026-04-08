import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Typography, TextField, InputAdornment,
    Grid, CircularProgress, Alert, Pagination,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { restaurantApi } from '../../api/restaurant';
import RestaurantCard from '../../components/restaurant/RestaurantCard';

export default function RestaurantListPage() {
    const navigate = useNavigate();
    const [data, setData] = useState({ items: [], total: 0 });
    const [page, setPage] = useState(1);
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const limit = 12;

    useEffect(() => {
        if (query.trim()) return;
        setLoading(true);
        restaurantApi.getAllPaginated(page, limit)
            .then(({ data }) => setData(data))
            .catch((err) => setError(err.response?.data?.detail || 'Failed to load restaurants'))
            .finally(() => setLoading(false));
    }, [page, query]);

    useEffect(() => {
        if (!query.trim()) return;
        setLoading(true);
        restaurantApi.search(query)
            .then(({ data }) => setData({ items: data, total: data.length }))
            .catch((err) => setError(err.response?.data?.detail || 'Search failed'))
            .finally(() => setLoading(false));
    }, [query]);

    const totalPages = Math.ceil(data.total / limit);

    return (
        <DashboardLayout>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 0.5 }}>Restaurants</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Browse and order from restaurants near you
            </Typography>
            <TextField
                fullWidth placeholder="Search restaurants…"
                value={query} onChange={(e) => { setQuery(e.target.value); setPage(1); }}
                InputProps={{ startAdornment: <InputAdornment position="start"><Search /></InputAdornment> }}
                sx={{ mb: 3, maxWidth: 480 }}
            />
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <>
                    <Grid container spacing={2}>
                        {data.items.map((r) => (
                            <Grid item xs={12} sm={6} md={4} key={r.id}>
                                <RestaurantCard
                                    restaurant={r}
                                    onClick={() => navigate(`/restaurants/${r.id}`)}
                                />
                            </Grid>
                        ))}
                    </Grid>
                    {!query && totalPages > 1 && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                            <Pagination count={totalPages} page={page} onChange={(_, v) => setPage(v)} />
                        </Box>
                    )}
                    {data.items.length === 0 && (
                        <Box sx={{ textAlign: 'center', py: 8 }}>
                            <Typography color="text.secondary">No restaurants found.</Typography>
                        </Box>
                    )}
                </>
            )}
        </DashboardLayout>
    );
}