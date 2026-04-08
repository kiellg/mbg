import { Box, Typography, IconButton, Stack } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { useCart } from '../../context/CartContext';

export default function CartItem({ item, restaurantId }) {
  const { updateItem, removeItem, loading } = useCart();

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', py: 2,
      borderBottom: '1px solid #EDE5D8', gap: 2 }}>

      <Box sx={{ flex: 1 }}>
        <Typography variant="body1" fontWeight={600} color="secondary">
          {item.item_name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {item.display_unit_price} each
        </Typography>
      </Box>

      <Stack direction="row" alignItems="center" spacing={0.5}>
        <IconButton size="small"
          disabled={loading || item.quantity <= 1}
          onClick={() => updateItem(restaurantId, item.id, { quantity: item.quantity - 1 })}
          sx={{ color: '#C0392B' }}>
          <RemoveIcon fontSize="small" />
        </IconButton>

        <Typography sx={{ minWidth: 24, textAlign: 'center', fontWeight: 600 }}>
          {item.quantity}
        </Typography>

        <IconButton size="small" disabled={loading}
          onClick={() => updateItem(restaurantId, item.id, { quantity: item.quantity + 1 })}
          sx={{ color: '#C0392B' }}>
          <AddIcon fontSize="small" />
        </IconButton>
      </Stack>

      <Typography variant="body1" fontWeight={700}
        sx={{ minWidth: 64, textAlign: 'right', color: '#1C2833' }}>
        {item.display_item_subtotal}
      </Typography>

      <IconButton size="small" disabled={loading}
        onClick={() => removeItem(restaurantId, item.id)}
        sx={{ color: '#5D6D7E', '&:hover': { color: '#C0392B' } }}>
        <DeleteOutlineIcon fontSize="small" />
      </IconButton>
    </Box>
  );
}