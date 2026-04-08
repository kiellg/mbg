import { Box, Typography } from '@mui/material';
import MenuItemCard from '../restaurant/MenuItemCard';

export default function MenuSection({ categoryName, items, restaurantId, onItemClick }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="body1" fontWeight={600}
        sx={{ mb: 1.5, pb: 1, borderBottom: '0.5px solid', borderColor: 'divider' }}>
        {categoryName}
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {items.map((item) => (
          <MenuItemCard
            key={item.id}
            item={item}
            onClick={onItemClick ? () => onItemClick(item) : undefined}
          />
        ))}
      </Box>
    </Box>
  );
}