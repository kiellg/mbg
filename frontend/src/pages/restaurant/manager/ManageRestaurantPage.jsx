import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box, Typography, TextField, Button,
    Alert, CircularProgress, Stack,
} from '@mui/material';
import { useRestaurant } from '../../../context/RestaurantContext';
import { restaurantApi } from '../../../api/restaurant';
import DashboardLayout from '../../../components/shared/DashboardLayout';
import { useAuth } from '../../../context/AuthContext'; // adjust path if needed



export default function ManageRestaurantPage() {
    const navigate = useNavigate();
    const { user } = useAuth(); // assumes { user: { id, ... } }
    const { createRestaurant, updateRestaurant, loading, error } = useRestaurant();
    const [restaurant, setRestaurant] = useState(null);
    const [fetching, setFetching] = useState(true);
    const [feedback, setFeedback] = useState(null);
    const [form, setForm] = useState({
        name: '', address: '', opening_hours: '', cuisine_type: '', rating: '',
    });



    useEffect(() => {
        restaurantApi.getAll()
            .then(({ data }) => {
                // Find the restaurant owned by the current manager, not just data[0],
                // to avoid loading another manager's restaurant when multiple exist.
                const owned = data.find((r) => String(r.owner_id) === String(user?.id));
                if (owned) {
                    setRestaurant(owned);
                    setForm({
                        name: owned.name ?? '',
                        address: owned.address ?? '',
                        opening_hours: owned.opening_hours ?? '',
                        cuisine_type: owned.cuisine_type ?? '',
                        rating: owned.rating ?? '',
                    });
                }
            })
            .finally(() => setFetching(false));
    }, [user?.id]);



    const handleChange = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));



    const handleSubmit = async (e) => {
        e.preventDefault();
        setFeedback(null);
        const payload = {
            ...form,
            rating: form.rating !== '' ? Number(form.rating) : null,
        };
        const result = restaurant
            ? await updateRestaurant(restaurant.id, payload)
            : await createRestaurant(payload);



        if (result.success) {
            setFeedback({ type: 'success', message: restaurant ? 'Restaurant updated.' : 'Restaurant created.' });
            if (!restaurant) setRestaurant(result.data);
        } else {
            setFeedback({ type: 'error', message: result.message });
        }
    };



    if (fetching) return (
        <DashboardLayout>
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress />
            </Box>
        </DashboardLayout>
    );



    return (
        <DashboardLayout>
            <Box sx={{ maxWidth: 600, mx: 'auto', px: 3, py: 4 }}>
                <Typography variant="h5" fontWeight={700} sx={{ mb: 0.5 }}>
                    {restaurant ? 'Edit Restaurant' : 'Create Restaurant'}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    {restaurant ? 'Update your restaurant details.' : 'Set up your restaurant profile.'}
                </Typography>
                {feedback && <Alert severity={feedback.type} sx={{ mb: 2 }}>{feedback.message}</Alert>}
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                <Box component="form" onSubmit={handleSubmit}>
                    <Stack spacing={2}>
                        <TextField label="Restaurant name" name="name" value={form.name} onChange={handleChange} required />
                        <TextField label="Address" name="address" value={form.address} onChange={handleChange} required />
                        <TextField label="Opening hours" name="opening_hours" placeholder="Mon-Sun 11:00-22:00"
                            value={form.opening_hours} onChange={handleChange} required />
                        <TextField label="Cuisine type" name="cuisine_type" value={form.cuisine_type} onChange={handleChange} />
                        <TextField label="Rating (1-5)" name="rating" type="number"
                            inputProps={{ min: 1, max: 5 }}
                            value={form.rating} onChange={handleChange} />
                        <Stack direction="row" spacing={2}>
                            <Button type="submit" variant="contained" disabled={loading}>
                                {loading ? 'Saving…' : restaurant ? 'Save changes' : 'Create restaurant'}
                            </Button>
                            {restaurant && (
                                <Button variant="outlined" onClick={() => navigate('/manager/restaurant/menu')}>
                                    Manage menu →
                                </Button>
                            )}
                        </Stack>
                    </Stack>
                </Box>
            </Box>
        </DashboardLayout>
    );
}