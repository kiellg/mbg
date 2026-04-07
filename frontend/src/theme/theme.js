import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#C0392B', dark: '#922B21', contrastText: '#fff' },
    secondary: { main: '#1C2833' },
    background: { default: '#F5F0EB', paper: '#FFFFFF' },
    text: { primary: '#1C2833', secondary: '#5D6D7E' },
    error: { main: '#C0392B' },
    success: { main: '#1E8449' },
  },
  typography: {
    fontFamily: '"Lora", Georgia, serif',
    h1: { fontFamily: '"Playfair Display", Georgia, serif', fontWeight: 700 },
    h2: { fontFamily: '"Playfair Display", Georgia, serif', fontWeight: 700 },
    h3: { fontFamily: '"Playfair Display", Georgia, serif', fontWeight: 600 },
    h4: { fontFamily: '"Playfair Display", Georgia, serif', fontWeight: 600 },
    button: { fontFamily: '"Lora", Georgia, serif', textTransform: 'none', fontWeight: 600 },
    body1: { fontFamily: '"Lora", Georgia, serif', fontSize: '0.95rem' },
    body2: { fontFamily: '"Lora", Georgia, serif', fontSize: '0.85rem' },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiTextField: {
      defaultProps: { variant: 'outlined', fullWidth: true, size: 'small' },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            backgroundColor: '#FDFBF8',
            '& fieldset': { borderColor: '#D5C9BA' },
            '&:hover fieldset': { borderColor: '#C0392B' },
            '&.Mui-focused fieldset': { borderColor: '#C0392B', borderWidth: 1.5 },
          },
          '& label.Mui-focused': { color: '#C0392B' },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 10, paddingTop: 10, paddingBottom: 10, fontSize: '0.9rem' },
        containedPrimary: {
          background: 'linear-gradient(135deg, #C0392B 0%, #922B21 100%)',
          boxShadow: '0 4px 16px rgba(192,57,43,0.25)',
          '&:hover': { boxShadow: '0 6px 20px rgba(192,57,43,0.35)' },
        },
      },
    },
    MuiCard: {
      styleOverrides: { root: { borderRadius: 16, boxShadow: '0 2px 24px rgba(28,40,51,0.08)' } },
    },
    MuiAlert: {
      styleOverrides: { root: { borderRadius: 10, fontSize: '0.85rem' } },
    },
    MuiChip: {
      styleOverrides: { root: { borderRadius: 8 } },
    },
  },
});

export default theme;