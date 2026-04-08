import { useState, useEffect, useRef } from 'react';
import { restaurantApi } from '../api/restaurant';

export function useSearchSuggestions() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef(null);

  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      setLoading(false);
      clearTimeout(debounceRef.current);
      return;
    }

    let isCancelled = false;

    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const { data } = await restaurantApi.getSuggestions(query);
        if (!isCancelled) {
            setSuggestions(data.suggestions || []);
        }
      } catch {
        if (!isCancelled) setSuggestions([]);
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }, 300);

    return () => {
        isCancelled = true;
        clearTimeout(debounceRef.current);
    };
  }, [query]);

  const clear = () => {
    setQuery('');
    setSuggestions([]);
    setLoading(false);
  };

  return { query, setQuery, suggestions, loading, clear };
}