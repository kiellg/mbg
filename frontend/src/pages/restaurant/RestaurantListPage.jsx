import { useNavigate } from 'react-router-dom';
import { Box, Typography, Alert, Skeleton } from '@mui/material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import SearchBar from '../../components/restaurant/SearchBar';
import RestaurantGrid from '../../components/restaurant/RestaurantGrid';
import RestaurantFilters from '../../components/restaurant/RestaurantFilters';
import Pagination from '../../components/shared/Pagination';
import RecentlyViewed from '../../components/shared/RecentlyViewed';
import { useRestaurants } from '../../hooks/useRestaurants';

export default function RestaurantListPage() {
  const navigate = useNavigate();
  const {
    restaurants, totalPages,
    page, setPage,
    sortBy, setSortBy,
    order, setOrder,
    cuisineTypes, setCuisineTypes,
    searchQuery, search,
    loading, error,
  } = useRestaurants();

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ mb: 0.5 }}>Search</Typography>
        <Typography variant="body2" color="text.secondary">
          Search for restaurants or dishes
        </Typography>
      </Box>

      <RecentlyViewed />

      <Box sx={{ mb: 2.5 }}>
        <SearchBar onSearch={search} />
      </Box>

      {!searchQuery && (
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
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {searchQuery && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Results for "<strong>{searchQuery}</strong>"
        </Typography>
      )}

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

      {!searchQuery && (
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      )}
    </DashboardLayout>
  );
}