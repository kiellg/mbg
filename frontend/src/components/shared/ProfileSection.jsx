import { Box, Typography, Paper } from '@mui/material';

export default function ProfileSection({ title, description, children }) {
  return (
    <Paper elevation={0} sx={{ border: '0.5px solid', borderColor: 'divider', borderRadius: 3, overflow: 'hidden', mb: 3 }}>
      <Box sx={{ px: 3, py: 2, borderBottom: '0.5px solid', borderColor: 'divider', bgcolor: 'rgba(0,0,0,0.01)' }}>
        <Typography variant="body1" fontWeight={600} color="text.primary">{title}</Typography>
        {description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.25 }}>{description}</Typography>
        )}
      </Box>
      <Box sx={{ px: 3, py: 2.5 }}>{children}</Box>
    </Paper>
  );
}