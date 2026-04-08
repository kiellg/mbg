import { Card, CardContent, Box, Typography, Chip, IconButton, Button } from '@mui/material';
import { Edit, Delete, AddShoppingCart } from '@mui/icons-material';

export default function MenuItemCard({ item, managerMode = false, onEdit, onDelete, onAddToCart }) {
  const price = item.price_cents != null
    ? `$${(item.price_cents / 100).toFixed(2)}`
    : 'Market price';

  // Don't allow adding to cart if price is invalid or item unavailable
  const canAddToCart = onAddToCart && item.price_cents != null && item.price_cents > 0 && item.is_available;

  return (
    <Card sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider' }} elevation={0}>
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1, mr: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Typography variant="body1" fontWeight={600} sx={{ fontSize: '0.95rem' }}>
                {item.name}
              </Typography>
              {item.dietary_tag && (
                <Chip label={item.dietary_tag} size="small" color="success" variant="outlined"
                  sx={{ fontSize: '0.65rem', height: 18 }} />
              )}
              {!item.is_active && (
                <Chip label="Inactive" size="small" color="default"
                  sx={{ fontSize: '0.65rem', height: 18 }} />
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
              <IconButton size="small" color="primary" onClick={() => onAddToCart(item)}
                title="Add to cart">
                <AddShoppingCart fontSize="small" />
              </IconButton>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}