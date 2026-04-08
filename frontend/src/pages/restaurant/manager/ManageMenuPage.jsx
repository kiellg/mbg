import { useEffect, useState } from 'react';
import {
    Box, Typography, Button, Stack, Alert, CircularProgress,
    Dialog, DialogTitle, DialogContent, DialogActions,
    TextField, MenuItem, Select, InputLabel, FormControl, Switch, FormControlLabel,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { restaurantApi } from '../../../api/restaurant';
import { useRestaurant } from '../../../context/RestaurantContext';
import MenuItemCard from '../../../components/restaurant/MenuItemCard';
import DashboardLayout from '../../../components/shared/DashboardLayout';
import { useAuth } from '../../../context/AuthContext';


const EMPTY_FORM = {
    name: '', description: '', price_cents: '', dietary_tag: '',
    category_id: '', is_visible: true, is_active: true, is_available: true,
};


export default function ManageMenuPage() {
    const { user } = useAuth();
    const { createMenuItem, updateMenuItem, deleteMenuItem, loading } = useRestaurant();
    const [restaurant, setRestaurant] = useState(null);
    const [categories, setCategories] = useState([]);
    const [dietaryTags, setDietaryTags] = useState([]);
    const [fetching, setFetching] = useState(true);
    const [feedback, setFeedback] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [editingItem, setEditingItem] = useState(null);
    const [form, setForm] = useState(EMPTY_FORM);


    useEffect(() => {
        Promise.all([restaurantApi.getAll(), restaurantApi.getCategories()])
            .then(([rRes, cRes]) => {
                setCategories(cRes.data.categories);
                setDietaryTags(cRes.data.dietary_tags);

                const ownedRestaurant = rRes.data.find(
                    (r) => String(r.owner_id) === String(user?.user_id),
                );

                if (!ownedRestaurant) {
                    setRestaurant(null);
                    return null;
                }

                return restaurantApi.getMenu(ownedRestaurant.id).then(({ data }) => {
                    setRestaurant(data);
                });
            })
            .finally(() => setFetching(false));
    }, [user?.user_id]);


    const openCreate = () => { setEditingItem(null); setForm(EMPTY_FORM); setDialogOpen(true); };
    const openEdit = (item) => {
        setEditingItem(item);
        setForm({
            name: item.name ?? '',
            description: item.description ?? '',
            price_cents: item.price_cents ?? '',
            dietary_tag: item.dietary_tag ?? '',
            category_id: item.category?.id ?? '',
            is_visible: item.is_visible ?? true,
            is_active: item.is_active ?? true,
            is_available: item.is_available ?? true,
        });
        setDialogOpen(true);
    };


    const handleChange = (e) => {
        const { name, value, checked, type } = e.target;
        setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
    };


    const handleSubmit = async () => {
        setFeedback(null);

        if (!form.price_cents || Number(form.price_cents) <= 0) {
            setFeedback({ type: 'error', message: 'Price is required and must be greater than 0.' });
            return;
        }
        if (!form.category_id) {
            setFeedback({ type: 'error', message: 'Category is required.' });
            return;
        }

        const payload = {
            ...form,
            price_cents: Number(form.price_cents),
            category_id: Number(form.category_id),
        };

        const result = editingItem
            ? await updateMenuItem(restaurant.id, editingItem.id, payload)
            : await createMenuItem(restaurant.id, payload);

        if (result.success) {
            const { data } = await restaurantApi.getMenu(restaurant.id);
            setRestaurant(data);
            setDialogOpen(false);
            setFeedback({ type: 'success', message: editingItem ? 'Item updated.' : 'Item added.' });
        } else {
            setFeedback({ type: 'error', message: result.message });
        }
    };


    const handleDelete = async (item) => {
        const result = await deleteMenuItem(restaurant.id, item.id);
        if (result.success) {
            const { data } = await restaurantApi.getMenu(restaurant.id);
            setRestaurant(data);
        }
    };


    if (fetching) return (
        <DashboardLayout>
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress />
            </Box>
        </DashboardLayout>
    );

    if (!restaurant) return (
        <DashboardLayout>
            <Alert severity="info" sx={{ m: 3 }}>No restaurant found. Create one first.</Alert>
        </DashboardLayout>
    );


    return (
        <DashboardLayout>
            <Box sx={{ maxWidth: 800, mx: 'auto', px: 3, py: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Box>
                        <Typography variant="h5" fontWeight={700}>{restaurant.name} — Menu</Typography>
                        <Typography variant="body2" color="text.secondary">Add, edit, or remove menu items</Typography>
                    </Box>
                    <Button variant="contained" startIcon={<Add />} onClick={openCreate}>Add item</Button>
                </Box>
                {feedback && <Alert severity={feedback.type} sx={{ mb: 2 }}>{feedback.message}</Alert>}
                {restaurant.menu?.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 8 }}>
                        <Typography color="text.secondary">No menu items yet. Add your first item.</Typography>
                    </Box>
                ) : (
                    <Stack spacing={1.5}>
                        {restaurant.menu?.map((item) => (
                            <MenuItemCard
                                key={item.id} item={item}
                                managerMode onEdit={openEdit} onDelete={handleDelete}
                            />
                        ))}
                    </Stack>
                )}

                {/* Add / Edit Dialog */}
                <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
                    <DialogTitle>{editingItem ? 'Edit menu item' : 'Add menu item'}</DialogTitle>
                    <DialogContent>
                        <Stack spacing={2} sx={{ mt: 1 }}>
                            <TextField label="Name" name="name" value={form.name} onChange={handleChange} required />
                            <TextField label="Description" name="description" value={form.description}
                                onChange={handleChange} multiline rows={2} />
                            <TextField
                                label="Price (cents)"
                                name="price_cents"
                                type="number"
                                value={form.price_cents}
                                onChange={handleChange}
                                required
                                inputProps={{ min: 1 }}
                                helperText="e.g. 1499 = $14.99"
                            />
                            <FormControl fullWidth required>
                                <InputLabel>Category</InputLabel>
                                <Select name="category_id" value={form.category_id} label="Category" onChange={handleChange}>
                                    {categories.map((c) => (
                                        <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            <FormControl fullWidth>
                                <InputLabel>Dietary tag</InputLabel>
                                <Select name="dietary_tag" value={form.dietary_tag} label="Dietary tag" onChange={handleChange}>
                                    <MenuItem value="">None</MenuItem>
                                    {dietaryTags.map((tag) => (
                                        <MenuItem key={tag} value={tag}>{tag}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            <Stack direction="row" spacing={2}>
                                <FormControlLabel control={<Switch name="is_visible" checked={form.is_visible} onChange={handleChange} />} label="Visible" />
                                <FormControlLabel control={<Switch name="is_active" checked={form.is_active} onChange={handleChange} />} label="Active" />
                                <FormControlLabel control={<Switch name="is_available" checked={form.is_available} onChange={handleChange} />} label="Available" />
                            </Stack>
                        </Stack>
                    </DialogContent>
                    <DialogActions sx={{ px: 3, pb: 2 }}>
                        <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
                            {loading ? 'Saving…' : editingItem ? 'Save changes' : 'Add item'}
                        </Button>
                    </DialogActions>
                </Dialog>
            </Box>
        </DashboardLayout>
    );
}
