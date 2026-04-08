import { useState, useEffect, useCallback } from 'react';
import { restaurantApi } from '../api/restaurant';

export function useRestaurants() {
  const [restaurants, setRestaurants] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [sortBy, setSortBy] = useState('rating');
  const [order, setOrder] = useState('desc');
  const [cuisineTypes, setCuisineTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (cuisineTypes.length > 0) {
        const { data } = await restaurantApi.filter(cuisineTypes);
        setRestaurants(data);
        setTotal(data.length);
      } else {
        const { data } = await restaurantApi.getAllPaginated(page, limit, sortBy, order);
        setRestaurants(data.items);
        setTotal(data.total);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load restaurants');
    } finally {
      setLoading(false);
    }
  }, [page, limit, sortBy, order, cuisineTypes]);

  useEffect(() => { fetch(); }, [fetch]);

  const search = useCallback(async (q) => {
    if (!q.trim()) { fetch(); return; }

    // Reset pagination state when searching
    setPage(1);
    setSortBy('rating');
    setOrder('desc');
    setLoading(true);
    setError(null);
    try {
      const { data } = await restaurantApi.search(q);
      setRestaurants(data);
      setTotal(data.length);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [fetch]);

  // Reset pagination when cuisine filter changes
  const handleSetCuisineTypes = useCallback((val) => {
    setPage(1);
    setSortBy('rating');
    setOrder('desc');
    setCuisineTypes(val);
  }, []);

  const totalPages = Math.ceil(total / limit);

  return {
    restaurants, total, totalPages,
    page, setPage,
    sortBy, setSortBy,
    order, setOrder,
    cuisineTypes, setCuisineTypes,
    setCuisineTypes: handleSetCuisineTypes,
    loading, error,
    search, refetch: fetch,
  };
}