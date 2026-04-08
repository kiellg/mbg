import { Grid, Typography, Box } from '@mui/material';
import RestaurantCard from './RestaurantCard';

export default function RestaurantGrid({ restaurants, loading, onCardClick }) {
  if (!loading && restaurants.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h4" sx={{ fontSize: '2rem', mb: 1 }}>🍽️</Typography>
        <Typography variant="body1" color="text.secondary">No restaurants found</Typography>
        <Typography variant="body2" color="text.secondary">
          Try a different search or filter
        </Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={2}>
      {restaurants.map((r) => (
        <Grid item xs={12} sm={6} md={4} key={r.id}>
          <RestaurantCard
            restaurant={r}
            onClick={onCardClick ? () => onCardClick(r) : undefined}
          />
        </Grid>
      ))}
    </Grid>
  );
}