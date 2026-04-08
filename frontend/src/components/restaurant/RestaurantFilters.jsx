import {
    Box, FormControl, InputLabel, Select, MenuItem,
    OutlinedInput, Chip, Typography, ToggleButton, ToggleButtonGroup,
  } from '@mui/material';
  import { SortOutlined } from '@mui/icons-material';
  
  const CUISINE_OPTIONS = [
    'Italian', 'Japanese', 'Chinese', 'Mexican', 'Indian',
    'Thai', 'American', 'Mediterranean', 'Korean', 'Vietnamese',
  ];
  
  export default function RestaurantFilters({
    cuisineTypes, setCuisineTypes,
    sortBy, setSortBy,
    order, setOrder,
  }) {
    const handleCuisineChange = (e) => {
      const val = e.target.value;
      setCuisineTypes(typeof val === 'string' ? val.split(',') : val);
    };
  
    const handleSortChange = (_, val) => {
      if (!val) return;
      const [newSortBy, newOrder] = val.split('-');
      setSortBy(newSortBy);
      setOrder(newOrder);
    };
  
    return (
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Cuisine type</InputLabel>
          <Select
            multiple
            value={cuisineTypes}
            onChange={handleCuisineChange}
            input={<OutlinedInput label="Cuisine type" />}
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((val) => (
                  <Chip key={val} label={val} size="small"
                    sx={{ height: 18, fontSize: '0.7rem', bgcolor: 'rgba(192,57,43,0.08)', color: '#C0392B' }} />
                ))}
              </Box>
            )}
            sx={{ borderRadius: 2.5 }}
          >
            {CUISINE_OPTIONS.map((c) => (
              <MenuItem key={c} value={c}>
                <Typography variant="body2">{c}</Typography>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
  
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SortOutlined sx={{ fontSize: 18, color: 'text.secondary' }} />
          <ToggleButtonGroup
            size="small" exclusive
            value={`${sortBy}-${order}`}
            onChange={handleSortChange}
            sx={{
              '& .MuiToggleButton-root': {
                px: 1.5, py: 0.5, fontSize: '0.75rem',
                borderRadius: '8px !important',
                border: '0.5px solid', borderColor: 'divider',
              },
            }}
          >
            <ToggleButton value="rating-desc">Top rated</ToggleButton>
            <ToggleButton value="rating-asc">Lowest rated</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>
    );
  }