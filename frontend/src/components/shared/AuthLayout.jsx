import { Box, Card, CardContent, Typography } from '@mui/material';

const patternBg = `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23C0392B' fill-opacity='0.06'%3E%3Cpath d='M30 5 C30 5 35 15 30 20 C25 15 30 5 30 5z'/%3E%3Ccircle cx='10' cy='10' r='3'/%3E%3Ccircle cx='50' cy='50' r='3'/%3E%3Ccircle cx='10' cy='50' r='2'/%3E%3Ccircle cx='50' cy='10' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`;

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: `${patternBg}, linear-gradient(160deg, #F5F0EB 0%, #EDE5D8 100%)`,
        px: 2,
        py: 4,
      }}
    >
      <Box sx={{ position: 'fixed', top: 24, left: 32 }}>
        <Typography
          sx={{
            fontFamily: '"Playfair Display", serif',
            fontSize: '1.4rem',
            fontWeight: 700,
            color: '#C0392B',
            letterSpacing: '-0.5px',
          }}
        >
          Chow
        </Typography>
      </Box>

      <Card sx={{ width: '100%', maxWidth: 440, overflow: 'visible' }}>
        <Box sx={{ height: 5, background: 'linear-gradient(90deg, #C0392B, #E74C3C)', borderRadius: '16px 16px 0 0' }} />
        <CardContent sx={{ px: 4, pt: 3.5, pb: 4 }}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h3" sx={{ fontSize: '1.75rem', color: '#1C2833', mb: 0.5 }}>
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          {children}
        </CardContent>
      </Card>
    </Box>
  );
}