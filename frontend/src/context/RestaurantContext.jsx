import { createContext, useContext, useState, useCallback } from 'react';
import { restaurantApi } from '../api/restaurant';

const RestaurantContext = createContext(null);

export function RestaurantProvider({ children }) {
    const [restaurants, setRestaurants] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const clearError = useCallback(() => setError(null), []);

    const fetchRestaurants = useCallback(async (page = 1, limit = 10) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await restaurantApi.getAllPaginated(page, limit);
            setRestaurants(data.items);
            return { success: true, data };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to load restaurants';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchMenu = useCallback(async (restaurantId) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await restaurantApi.getMenu(restaurantId);
            return { success: true, data };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to load menu';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const createRestaurant = useCallback(async (payload) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await restaurantApi.create(payload);
            return { success: true, data };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to create restaurant';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const updateRestaurant = useCallback(async (restaurantId, payload) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await restaurantApi.update(restaurantId, payload);
            return { success: true, data };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to update restaurant';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteRestaurant = useCallback(async (restaurantId) => {
        setLoading(true);
        setError(null);
        try {
            await restaurantApi.delete(restaurantId);
            return { success: true };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to delete restaurant';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const createMenuItem = useCallback(async (restaurantId, payload) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await restaurantApi.createMenuItem(restaurantId, payload);
            return { success: true, data };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to create menu item';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const updateMenuItem = useCallback(async (restaurantId, itemId, payload) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await restaurantApi.updateMenuItem(restaurantId, itemId, payload);
            return { success: true, data };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to update menu item';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteMenuItem = useCallback(async (restaurantId, itemId) => {
        setLoading(true);
        setError(null);
        try {
            await restaurantApi.deleteMenuItem(restaurantId, itemId);
            return { success: true };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to delete menu item';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    return (
        <RestaurantContext.Provider value={{
            restaurants, loading, error, clearError,
            fetchRestaurants, fetchMenu,
            createRestaurant, updateRestaurant, deleteRestaurant,
            createMenuItem, updateMenuItem, deleteMenuItem,
        }}>
            {children}
        </RestaurantContext.Provider>
    );
}

export const useRestaurant = () => {
    const ctx = useContext(RestaurantContext);
    if (!ctx) throw new Error('useRestaurant must be used inside RestaurantProvider');
    return ctx;
};