import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, TextField, Paper, List, ListItem,
  ListItemText, Typography, InputAdornment,
  IconButton, Divider, CircularProgress,
} from '@mui/material';
import {
  SearchOutlined, CloseOutlined,
  RestaurantOutlined, MenuBookOutlined,
} from '@mui/icons-material';
import { useSearchSuggestions } from '../../hooks/useSearchSuggestions';

export default function SearchBar({ onSearch }) {
  const navigate = useNavigate();
  const { query, setQuery, suggestions, loading, clear } = useSearchSuggestions();
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef(null);
  const [activeIndex, setActiveIndex] = useState(-1);

  useEffect(() => {
    const handleClick = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  useEffect(() => {
    setOpen(suggestions.length > 0);
  }, [suggestions]);

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
        setActiveIndex(prev => Math.min(prev + 1, suggestions.length - 1));
      } else if (e.key === 'ArrowUp') {
        setActiveIndex(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        if (activeIndex >= 0 && suggestions[activeIndex]) {
          handleSuggestionClick(suggestions[activeIndex]);
        } else if (query.trim()) {
          setOpen(false);
          onSearch?.(query);
        }
      } else if (e.key === 'Escape') {
        setOpen(false);
        setActiveIndex(-1);
    }
  };

  const handleSuggestionClick = (s) => {
    clear();
    setOpen(false);
    if (s.suggestion_type === 'restaurant') {
      navigate(`/restaurants/${s.id}`);
    } else {
      navigate(`/restaurants/${s.restaurant_id}/menu/${s.id}`);
    }
  };

  const restaurantSuggestions = suggestions.filter(s => s.suggestion_type === 'restaurant');
  const menuSuggestions = suggestions.filter(s => s.suggestion_type === 'menu_item');

  return (
    <Box ref={wrapperRef} sx={{ position: 'relative', width: '100%' }}>
      <TextField
        fullWidth
        placeholder="Search restaurants or dishes…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => suggestions.length > 0 && setOpen(true)}
        size="small"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              {loading
                ? <CircularProgress size={16} />
                : <SearchOutlined sx={{ fontSize: 18, color: 'text.secondary' }} />
              }
            </InputAdornment>
          ),
          endAdornment: query && (
            <InputAdornment position="end">
              <IconButton size="small" onClick={() => { clear(); onSearch?.(''); }}>
                <CloseOutlined sx={{ fontSize: 16 }} />
              </IconButton>
            </InputAdornment>
          ),
          sx: { borderRadius: 3, bgcolor: 'background.paper' },
        }}
      />

      {open && (
        <Paper elevation={0} sx={{
          position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
          mt: 0.5, border: '0.5px solid', borderColor: 'divider',
          borderRadius: 3, overflow: 'hidden', maxHeight: 360, overflowY: 'auto',
        }}>
          {restaurantSuggestions.length > 0 && (
            <>
              <Box sx={{ px: 2, py: 1, bgcolor: 'rgba(0,0,0,0.02)' }}>
                <Typography variant="caption" color="text.secondary" fontWeight={600}
                  sx={{ textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Restaurants
                </Typography>
              </Box>
              <List dense disablePadding>
                {restaurantSuggestions.map((s) => (
                    <ListItem
                        key={`r-${s.id}`}
                        button
                        selected={getGlobalIndex(s) === activeIndex}
                        onClick={() => handleSuggestionClick(s)}
                        sx={{
                            '&:hover': { bgcolor: 'rgba(192,57,43,0.05)' },
                            '&.Mui-selected': { bgcolor: 'rgba(192,57,43,0.08)' },
                            '&.Mui-selected:hover': { bgcolor: 'rgba(192,57,43,0.1)' },
                        }}
                        >
                        <RestaurantOutlined sx={{ fontSize: 16, color: 'text.secondary', mr: 1.5 }} />
                        <ListItemText primary={s.name} primaryTypographyProps={{ variant: 'body2' }} />
                    </ListItem>
                ))}
              </List>
            </>
          )}

          {restaurantSuggestions.length > 0 && menuSuggestions.length > 0 && <Divider />}

          {menuSuggestions.length > 0 && (
            <>
              <Box sx={{ px: 2, py: 1, bgcolor: 'rgba(0,0,0,0.02)' }}>
                <Typography variant="caption" color="text.secondary" fontWeight={600}
                  sx={{ textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Dishes
                </Typography>
              </Box>
              <List dense disablePadding>
                {menuSuggestions.map((s) => (
                    <ListItem
                        key={`m-${s.id}`}
                        button
                        selected={getGlobalIndex(s) === activeIndex}
                        onClick={() => handleSuggestionClick(s)}
                        sx={{
                            '&:hover': { bgcolor: 'rgba(192,57,43,0.05)' },
                            '&.Mui-selected': { bgcolor: 'rgba(192,57,43,0.08)' },
                            '&.Mui-selected:hover': { bgcolor: 'rgba(192,57,43,0.1)' },
                        }}
                        >
                        <MenuBookOutlined sx={{ fontSize: 16, color: 'text.secondary', mr: 1.5 }} />
                        <ListItemText primary={s.name} primaryTypographyProps={{ variant: 'body2' }} />
                    </ListItem>
                ))}
              </List>
            </>
          )}
        </Paper>
      )}
    </Box>
  );
}