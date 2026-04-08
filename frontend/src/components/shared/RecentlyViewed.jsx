import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, Skeleton } from '@mui/material';
import { HistoryOutlined } from '@mui/icons-material';
import { recentlyViewedApi } from '../../api/recentlyViewed';
import { restaurantApi } from '../../api/restaurant';
import { useAuth } from '../../context/AuthContext';

export default function RecentlyViewed() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [enriched, setEnriched] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    setLoading(true);

    recentlyViewedApi.getRecentlyViewed()
      .then(async ({ data }) => {
        const items = data.items || [];

        const seen = new Set();
        const unique = items.filter(item => {
          const key = `${item.type}:${item.id}`;
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        }).slice(0, 8);

        const results = await Promise.allSettled(
          unique.map(async (item) => {
            if (item.type === 'restaurant') {
              try {
                const { data: restaurant } = await restaurantApi.getMenu(item.id);
                return { ...item, name: restaurant.name };
              } catch {
                return { ...item, name: `Restaurant #${item.id}` };
              }
            }
            // For menu items, just show a generic label
            return { ...item, name: `Menu item #${item.id}` };
          })
        );

        setEnriched(results
          .filter(r => r.status === 'fulfilled')
          .map(r => r.value)
        );
      })
      .catch(() => setEnriched([]))
      .finally(() => setLoading(false));
  }, [user]);

  if (!user || (!loading && enriched.length === 0)) return null;

  const handleClick = (item) => {
    if (item.type === 'restaurant') {
      navigate(`/restaurants/${item.id}`);
    }
  };

  const restaurantItems = enriched.filter(item => item.type === 'restaurant');

  if (!loading && restaurantItems.length === 0) return null;

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
            <Skeleton key={i} variant="rounded" width={140} height={40}
              sx={{ borderRadius: 2, flexShrink: 0 }} />
          ))
          : restaurantItems.map((item) => (
            <Paper key={`${item.type}-${item.id}`} elevation={0} onClick={() => handleClick(item)}
              sx={{
                px: 1.5, py: 1, borderRadius: 2, flexShrink: 0,
                border: '0.5px solid', borderColor: 'divider',
                cursor: 'pointer', transition: 'all 0.15s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'rgba(192,57,43,0.04)' },
              }}
            >
              <Typography variant="caption" fontWeight={500} color="text.primary" noWrap
                sx={{ maxWidth: 140, display: 'block' }}>
                🍽️ {item.name}
              </Typography>
            </Paper>
          ))
        }
      </Box>
    </Box>
  );
}