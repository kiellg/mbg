import { useState, useEffect, useCallback } from 'react';
import { restaurantApi } from '../api/restaurant';

export function useRestaurants() {
  const [restaurants, setRestaurants] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [sortBy, setSortBy] = useState('rating');
  const [order, setOrder] = useState('desc');
  const [cuisineTypes, _setCuisineTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Search mode
      if (searchQuery.trim()) {
        const { data } = await restaurantApi.search(searchQuery);
        setRestaurants(data);
        setTotal(data.length);
      // Filter mode
      } else if (cuisineTypes.length > 0) {
        const { data } = await restaurantApi.filter(cuisineTypes);
        setRestaurants(data);
        setTotal(data.length);
      // Default paginated mode
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
  }, [searchQuery, cuisineTypes, page, limit, sortBy, order]);

  useEffect(() => { fetch(); }, [fetch]);

  // Search — resets pagination and filter state
  const search = useCallback((q) => {
    setSearchQuery(q);
    setPage(1);
    setSortBy('rating');
    setOrder('desc');
    _setCuisineTypes([]);
  }, []);

  // Cuisine filter — resets pagination and clears search
  const setCuisineTypes = useCallback((val) => {
    _setCuisineTypes(val);
    setSearchQuery('');
    setPage(1);
    setSortBy('rating');
    setOrder('desc');
  }, []);

  const totalPages = Math.ceil(total / limit);

  return {
    restaurants, total, totalPages,
    page, setPage,
    sortBy, setSortBy,
    order, setOrder,
    cuisineTypes, setCuisineTypes,
    searchQuery, search,
    loading, error,
    refetch: fetch,
  };
}