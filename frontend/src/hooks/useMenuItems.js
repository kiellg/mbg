import { useState, useEffect, useCallback } from 'react';
import { restaurantApi } from '../api/restaurant';

export function useMenuItems(restaurantId) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [sortBy, setSortBy] = useState('price');
  const [order, setOrder] = useState('asc');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    if (!restaurantId) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await restaurantApi.getMenuPaginatedSorted(
        restaurantId, page, limit, sortBy, order
      );
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load menu');
    } finally {
      setLoading(false);
    }
  }, [restaurantId, page, limit, sortBy, order]);

  useEffect(() => { fetch(); }, [fetch]);

  const totalPages = Math.ceil(total / limit);

  return {
    items, total, totalPages,
    page, setPage,
    sortBy, setSortBy,
    order, setOrder,
    loading, error,
    refetch: fetch,
  };
}