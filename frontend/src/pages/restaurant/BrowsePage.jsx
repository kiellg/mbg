import { useNavigate } from 'react-router-dom';
import { Box, Typography, Skeleton, Alert } from '@mui/material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import RestaurantGrid from '../../components/restaurant/RestaurantGrid';
import RestaurantFilters from '../../components/restaurant/RestaurantFilters';
import Pagination from '../../components/shared/Pagination';
import { useRestaurants } from '../../hooks/useRestaurants';

export default function BrowsePage() {
  const navigate = useNavigate();
  const {
    restaurants, totalPages,
    page, setPage,
    sortBy, setSortBy,
    order, setOrder,
    cuisineTypes, setCuisineTypes,
    loading, error,
  } = useRestaurants();

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ mb: 0.5 }}>Home</Typography>
        <Typography variant="body2" color="text.secondary">
          Discover places to eat near you
        </Typography>
      </Box>

      <Box sx={{ mb: 3 }}>
        <RestaurantFilters
          cuisineTypes={cuisineTypes}
          setCuisineTypes={setCuisineTypes}
          sortBy={sortBy}
          setSortBy={(val) => { setSortBy(val); setPage(1); }}
          order={order}
          setOrder={(val) => { setOrder(val); setPage(1); }}
        />
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 2 }}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Skeleton key={i} variant="rounded" height={160} sx={{ borderRadius: 3 }} />
          ))}
        </Box>
      ) : (
        <RestaurantGrid
          restaurants={restaurants}
          loading={loading}
          onCardClick={(r) => navigate(`/restaurants/${r.id}`)}
        />
      )}

      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </DashboardLayout>
  );
}