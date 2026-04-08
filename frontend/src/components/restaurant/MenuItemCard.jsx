import { Card, CardContent, Box, Typography, Chip, IconButton } from '@mui/material';
import { Edit, Delete, AddShoppingCart } from '@mui/icons-material';

const DIETARY_COLORS = {
  vegan:       { bg: 'rgba(30,132,73,0.1)',  color: '#1E8449' },
  vegetarian:  { bg: 'rgba(30,132,73,0.08)', color: '#1E8449' },
  halal:       { bg: 'rgba(26,82,118,0.1)',  color: '#1A5276' },
  gluten_free: { bg: 'rgba(142,68,173,0.1)', color: '#7D3C98' },
};

export default function MenuItemCard({ item, managerMode = false, onEdit, onDelete, onAddToCart, onClick, }) {
  const price = item.price_cents != null
    ? `$${(item.price_cents / 100).toFixed(2)}`
    : 'Market price';

  const unavailable = !item.is_available || !item.is_active;
  const dietaryStyle = item.dietary_tag ? DIETARY_COLORS[item.dietary_tag] : null;

  // Don't allow adding to cart if price is invalid or item unavailable
  const canAddToCart = onAddToCart && item.price_cents != null && item.price_cents > 0 && item.is_available;

  return (
    <Card
      elevation={0}
      onClick={!managerMode ? onClick : undefined}
      sx={{
        borderRadius: 2, border: '1px solid', borderColor: 'divider',
        opacity: unavailable ? 0.55 : 1,
        cursor: !managerMode && onClick ? 'pointer' : 'default',
        transition: 'all 0.15s',
        '&:hover': !managerMode && onClick ? { borderColor: 'primary.main' } : {},
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1, mr: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, flexWrap: 'wrap' }}>
              <Typography variant="body1" fontWeight={600} sx={{ fontSize: '0.95rem' }}>
                {item.name}
              </Typography>
              {item.dietary_tag && dietaryStyle && (
                <Chip
                  label={item.dietary_tag.replace('_', ' ')}
                  size="small"
                  sx={{ fontSize: '0.65rem', height: 18, bgcolor: dietaryStyle.bg, color: dietaryStyle.color, fontWeight: 500 }}
                />
              )}
              {item.category && (
                <Chip
                  label={item.category.name}
                  size="small"
                  sx={{ fontSize: '0.65rem', height: 18, bgcolor: 'rgba(0,0,0,0.05)', color: 'text.secondary' }}
                />
              )}
              {!item.is_active && (
                <Chip label="Inactive" size="small" color="default" sx={{ fontSize: '0.65rem', height: 18 }} />
              )}
              {!item.is_available && (
                <Chip label="Unavailable" size="small" color="default" sx={{ fontSize: '0.65rem', height: 18 }} />
              )}
            </Box>
            {item.description && (
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem', mb: 0.5 }}>
                {item.description}
              </Typography>
            )}
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
            <Typography variant="body1" fontWeight={700} color="primary.main">
              {price}
            </Typography>

            {managerMode && (
              <>
                <IconButton size="small" onClick={() => onEdit(item)}>
                  <Edit fontSize="small" />
                </IconButton>
                <IconButton size="small" color="error" onClick={() => onDelete(item)}>
                  <Delete fontSize="small" />
                </IconButton>
              </>
            )}

            {canAddToCart && (
              <IconButton
                size="small"
                color="primary"
                onClick={(e) => { e.stopPropagation(); onAddToCart(item); }}
                title="Add to cart"
              >
                <AddShoppingCart fontSize="small" />
              </IconButton>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}