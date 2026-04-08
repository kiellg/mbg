import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, Skeleton } from '@mui/material';
import { HistoryOutlined } from '@mui/icons-material';
import { recentlyViewedApi } from '../../api/recentlyViewed';
import { useAuth } from '../../context/AuthContext';

export default function RecentlyViewed() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    recentlyViewedApi.getRecentlyViewed()
      .then(({ data }) => setItems(data.items || []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [user]);

  if (!user || (!loading && items.length === 0)) return null;

  const handleClick = (item) => {
    if (item.type === 'restaurant') {
      navigate(`/restaurants/${item.id}`);
    } else {
      navigate('/restaurants');
    }
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
        <HistoryOutlined sx={{ fontSize: 16, color: 'text.secondary' }} />
        <Typography variant="body2" color="text.secondary" fontWeight={600}
          sx={{ textTransform: 'uppercase', letterSpacing: '0.06em', fontSize: '0.7rem' }}>
          Recently viewed
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 1.5, overflowX: 'auto', pb: 1 }}>
        {loading
          ? [1, 2, 3].map(i => (
            <Skeleton key={i} variant="rounded" width={120} height={40}
              sx={{ borderRadius: 2, flexShrink: 0 }} />
          ))
          : items.slice(0, 8).map((item, i) => (
            <Paper key={i} elevation={0} onClick={() => handleClick(item)}
              sx={{
                px: 1.5, py: 1, borderRadius: 2, flexShrink: 0,
                border: '0.5px solid', borderColor: 'divider',
                cursor: 'pointer', transition: 'all 0.15s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'rgba(192,57,43,0.04)' },
              }}
            >
              <Typography variant="caption" fontWeight={500} color="text.primary">
                {item.type === 'restaurant' ? '🍽️' : '🍜'} {item.type} #{item.id}
              </Typography>
            </Paper>
          ))
        }
      </Box>
    </Box>
  );
}