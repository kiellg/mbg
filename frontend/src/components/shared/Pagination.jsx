import { Box, Button, Typography } from '@mui/material';
import { ChevronLeftOutlined, ChevronRightOutlined } from '@mui/icons-material';

export default function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, mt: 3 }}>
      <Button
        size="small" variant="outlined"
        startIcon={<ChevronLeftOutlined />}
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        sx={{ borderRadius: 2, borderColor: 'divider', color: 'text.secondary' }}
      >
        Prev
      </Button>

      <Typography variant="body2" color="text.secondary">
        Page <strong>{page}</strong> of <strong>{totalPages}</strong>
      </Typography>

      <Button
        size="small" variant="outlined"
        endIcon={<ChevronRightOutlined />}
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        sx={{ borderRadius: 2, borderColor: 'divider', color: 'text.secondary' }}
      >
        Next
      </Button>
    </Box>
  );
}