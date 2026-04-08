import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Alert, Skeleton,
  Chip, Button, Paper, Divider,
} from '@mui/material';
import {
  ArrowBackOutlined, BlockOutlined,
  CheckCircleOutlined, LocalOfferOutlined,
} from '@mui/icons-material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { restaurantApi } from '../../api/restaurant';

const DIETARY_COLORS = {
  vegan:       { bg: 'rgba(30,132,73,0.1)',  color: '#1E8449' },
  vegetarian:  { bg: 'rgba(30,132,73,0.08)', color: '#1E8449' },
  halal:       { bg: 'rgba(26,82,118,0.1)',  color: '#1A5276' },
  gluten_free: { bg: 'rgba(142,68,173,0.1)', color: '#7D3C98' },
};

export default function MenuItemDetailPage() {
  const { id, itemId } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    restaurantApi.getMenuItem(id, itemId)
      .then(({ data }) => setItem(data))
      .catch((err) => setError(err.response?.data?.detail || 'Item not found'))
      .finally(() => setLoading(false));
  }, [id, itemId]);

  const unavailable = item && (!item.is_available || !item.is_active);
  const dietaryStyle = item?.dietary_tag ? DIETARY_COLORS[item.dietary_tag] : null;

  return (
    <DashboardLayout>
      <Button
        startIcon={<ArrowBackOutlined />}
        onClick={() => navigate(`/restaurants/${id}`)}
        sx={{ mb: 2.5, color: 'text.secondary', fontWeight: 400, pl: 0 }}
      >
        Back to menu
      </Button>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Skeleton height={36} width="50%" />
          <Skeleton height={24} width="30%" />
          <Skeleton height={80} />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : item && (
        <Paper elevation={0} sx={{ border: '0.5px solid', borderColor: 'divider', borderRadius: 3, overflow: 'hidden' }}>
          <Box sx={{ px: 3, py: 2.5, borderBottom: '0.5px solid', borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}>
              <Typography variant="h4" sx={{ fontSize: '1.4rem' }}>{item.name}</Typography>
              <Box sx={{ textAlign: 'right', flexShrink: 0 }}>
                {unavailable ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <BlockOutlined sx={{ fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">Unavailable</Typography>
                  </Box>
                ) : item.display_price ? (
                  <Typography variant="h4" sx={{ fontSize: '1.4rem', color: '#C0392B', fontWeight: 700 }}>
                    {item.display_price}
                  </Typography>
                ) : item.price_cents != null ? (
                  <Typography variant="h4" sx={{ fontSize: '1.4rem', color: '#C0392B', fontWeight: 700 }}>
                    ${(item.price_cents / 100).toFixed(2)}
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.secondary">Price TBD</Typography>
                )}
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 1, mt: 1.5, flexWrap: 'wrap' }}>
              {item.category && (
                <Chip label={item.category.name} size="small"
                  sx={{ height: 22, fontSize: '0.75rem', bgcolor: 'rgba(0,0,0,0.05)', color: 'text.secondary' }} />
              )}
              {item.dietary_tag && dietaryStyle && (
                <Chip label={item.dietary_tag.replace('_', ' ')} size="small"
                  sx={{ height: 22, fontSize: '0.75rem', bgcolor: dietaryStyle.bg, color: dietaryStyle.color, fontWeight: 500 }} />
              )}
            </Box>
          </Box>

          {item.description && (
            <Box sx={{ px: 3, py: 2, borderBottom: '0.5px solid', borderColor: 'divider' }}>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                {item.description}
              </Typography>
            </Box>
          )}

          <Box sx={{ px: 3, py: 2 }}>
            {[
              {
                label: 'Availability',
                value: unavailable ? 'Not available' : 'Available',
                icon: unavailable
                  ? <BlockOutlined sx={{ fontSize: 16, color: 'text.secondary' }} />
                  : <CheckCircleOutlined sx={{ fontSize: 16, color: '#1E8449' }} />,
              },
              {
                label: 'Price',
                value: item.display_price
                  || (item.price_cents != null ? `$${(item.price_cents / 100).toFixed(2)}` : 'Not set'),
                icon: <LocalOfferOutlined sx={{ fontSize: 16, color: 'text.secondary' }} />,
              },
            ].map(({ label, value, icon }) => (
              <Box key={label}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, py: 1.25 }}>
                  {icon}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="caption" color="text.secondary" display="block">{label}</Typography>
                    <Typography variant="body2" fontWeight={500}>{value}</Typography>
                  </Box>
                </Box>
                <Divider />
              </Box>
            ))}
          </Box>
        </Paper>
      )}
    </DashboardLayout>
  );
}