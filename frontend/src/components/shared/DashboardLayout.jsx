import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Avatar, Chip, Divider,
  IconButton, Drawer, useMediaQuery, useTheme,
} from '@mui/material';
import {
  PersonOutlined, StoreOutlined, TwoWheelerOutlined,
  LogoutOutlined, MenuOutlined,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';

const SIDEBAR_WIDTH = 240;

const ROLE_NAV = {
  customer: [{ label: 'My Profile',        to: '/profile/customer', icon: <PersonOutlined fontSize="small" /> }],
  manager:  [{ label: 'Restaurant Profile', to: '/profile/manager',  icon: <StoreOutlined fontSize="small" /> }],
  driver:   [{ label: 'Driver Profile',     to: '/profile/driver',   icon: <TwoWheelerOutlined fontSize="small" /> }],
};

const ROLE_META = {
  customer: { label: 'Customer', emoji: '🛍️', color: '#C0392B' },
  manager:  { label: 'Manager',  emoji: '🏪', color: '#1A5276' },
  driver:   { label: 'Driver',   emoji: '🚴', color: '#1E8449' },
};

function SidebarContent({ user, onLogout }) {
  const meta = ROLE_META[user?.role] || { label: 'User', emoji: '👤', color: '#555' };
  const navItems = ROLE_NAV[user?.role] || [];
  const initials = user?.email?.slice(0, 2).toUpperCase() ?? '??';

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', p: 2.5 }}>
      <Typography
        sx={{ fontFamily: '"Playfair Display", serif', fontSize: '1.3rem', fontWeight: 700, color: '#C0392B', mb: 3 }}
      >
        Chow
      </Typography>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, p: 1.5, borderRadius: 3, bgcolor: 'rgba(192,57,43,0.05)', border: '1px solid rgba(192,57,43,0.1)', mb: 2.5 }}>
        <Avatar sx={{ width: 38, height: 38, bgcolor: meta.color, fontSize: '0.85rem', fontWeight: 700 }}>
          {initials}
        </Avatar>
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 130 }}>{user?.email}</Typography>
          <Chip label={`${meta.emoji} ${meta.label}`} size="small"
            sx={{ height: 18, fontSize: '0.65rem', bgcolor: `${meta.color}18`, color: meta.color, fontWeight: 600, border: 'none' }} />
        </Box>
      </Box>

      <Divider sx={{ mb: 1.5 }} />

      <Typography variant="caption" color="text.secondary"
        sx={{ px: 1, mb: 0.5, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
        Account
      </Typography>

      {navItems.map((item) => (
        <NavLink key={item.to} to={item.to} style={{ textDecoration: 'none' }}>
          {({ isActive }) => (
            <Box sx={{
              display: 'flex', alignItems: 'center', gap: 1.5,
              px: 1.5, py: 1, borderRadius: 2, mb: 0.5,
              bgcolor: isActive ? 'rgba(192,57,43,0.08)' : 'transparent',
              color: isActive ? '#C0392B' : 'text.secondary',
              fontFamily: '"Lora", serif', fontSize: '0.875rem',
              fontWeight: isActive ? 600 : 400, transition: 'all 0.15s',
              '&:hover': { bgcolor: 'rgba(192,57,43,0.05)', color: '#C0392B' },
            }}>
              {item.icon}
              {item.label}
            </Box>
          )}
        </NavLink>
      ))}

      <Box sx={{ flex: 1 }} />
      <Divider sx={{ mb: 1.5 }} />

      <Box onClick={onLogout} sx={{
        display: 'flex', alignItems: 'center', gap: 1.5,
        px: 1.5, py: 1, borderRadius: 2, color: 'error.main',
        cursor: 'pointer', fontSize: '0.875rem',
        fontFamily: '"Lora", serif', fontWeight: 500,
        transition: 'all 0.15s',
        '&:hover': { bgcolor: 'rgba(192,57,43,0.06)' },
      }}>
        <LogoutOutlined fontSize="small" />
        Sign out
      </Box>
    </Box>
  );
}

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const muiTheme = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const sidebar = <SidebarContent user={user} onLogout={handleLogout} />;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#F5F0EB' }}>
      {!isMobile && (
        <Box sx={{
          width: SIDEBAR_WIDTH, flexShrink: 0, bgcolor: 'background.paper',
          borderRight: '0.5px solid', borderColor: 'divider',
          position: 'fixed', top: 0, left: 0, height: '100vh', overflowY: 'auto',
        }}>
          {sidebar}
        </Box>
      )}

      {isMobile && (
        <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)}
          PaperProps={{ sx: { width: SIDEBAR_WIDTH } }}>
          {sidebar}
        </Drawer>
      )}

      <Box sx={{ flex: 1, ml: isMobile ? 0 : `${SIDEBAR_WIDTH}px`, display: 'flex', flexDirection: 'column' }}>
        {isMobile && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, px: 2, py: 1.5, bgcolor: 'background.paper', borderBottom: '0.5px solid', borderColor: 'divider' }}>
            <IconButton size="small" onClick={() => setDrawerOpen(true)}><MenuOutlined /></IconButton>
            <Typography sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 700, color: '#C0392B' }}>
              Chow
            </Typography>
          </Box>
        )}
        <Box sx={{ p: { xs: 2.5, md: 4 }, maxWidth: 720, width: '100%' }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}