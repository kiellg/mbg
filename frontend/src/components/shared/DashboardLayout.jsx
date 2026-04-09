import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Avatar,
  Chip,
  Divider,
  IconButton,
  Drawer,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  PersonOutlined, StoreOutlined, TwoWheelerOutlined,
  DashboardOutlined, GroupOutlined, ConfirmationNumberOutlined,
  LogoutOutlined, MenuOutlined, RestaurantOutlined,
  FavoriteOutlined, MenuBookOutlined, HomeOutlined, SearchOutlined,
  ReceiptLongOutlined, LocalShippingOutlined, NotificationsOutlined,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationsContext';

const SIDEBAR_WIDTH = 240;

const ROLE_NAV = {
  admin: [
    {
      label: "Dashboard",
      to: "/admin",
      icon: <DashboardOutlined fontSize="small" />,
    },
    {
      label: "Users",
      to: "/admin/users",
      icon: <GroupOutlined fontSize="small" />,
    },
    {
      label: "Coupons",
      to: "/admin/coupons",
      icon: <ConfirmationNumberOutlined fontSize="small" />,
    },
  ],
  customer: [
    {
        label: "Home",
        to: "/restaurants/browse",
        icon: <HomeOutlined fontSize="small" />,
    },
    {
        label: "Search",
        to: "/restaurants",
        icon: <SearchOutlined fontSize="small" />,
    },
    {
      label: "My Profile",
      to: "/profile/customer",
      icon: <PersonOutlined fontSize="small" />,
    },
    {
      label: "Favourites",
      to: "/favourites",
      icon: <FavoriteOutlined fontSize="small" />,
    },
    {
    label: "My Orders",
    to: "/orders",
    icon: <ReceiptLongOutlined fontSize="small" />,
    },
    {
      label: "Notifications",
      to: "/notifications",
      icon: <NotificationsOutlined fontSize="small" />,
    },
  ],
  manager: [
    {
        label: "Home",
        to: "/restaurants/browse",
        icon: <HomeOutlined fontSize="small" />,
    },
    {
        label: "Search",
        to: "/restaurants",
        icon: <SearchOutlined fontSize="small" />,
    },
    {
      label: "Manage Restaurant",
      to: "/manage/restaurant",
      icon: <RestaurantOutlined fontSize="small" />,
    },
    {
      label: "Manage Menu",
      to: "/manage/menu",
      icon: <MenuBookOutlined fontSize="small" />,
    },
    {
      label: "Kitchen Queue",
      to: "/manager/kitchen-queue",
      icon: <LocalShippingOutlined fontSize="small" />,
    },
    {
      label: "Notifications",
      to: "/notifications",
      icon: <NotificationsOutlined fontSize="small" />,
    },
  ],
  driver: [
    {
        label: "Home",
        to: "/restaurants/browse",
        icon: <HomeOutlined fontSize="small" />,
    },
    {
        label: "Search",
        to: "/restaurants",
        icon: <SearchOutlined fontSize="small" />,
    },
    {
      label: "Driver Profile",
      to: "/profile/driver",
      icon: <TwoWheelerOutlined fontSize="small" />,
    },
    {
      label: "My Deliveries",
      to: "/deliveries",
      icon: <LocalShippingOutlined fontSize="small" />,
    },
    {
      label: "Notifications",
      to: "/notifications",
      icon: <NotificationsOutlined fontSize="small" />,
    },
  ],
};

const ROLE_META = {
  admin: { label: 'Admin', color: '#7D6608' },
  customer: { label: 'Customer', color: '#C0392B' },
  manager: { label: 'Manager', color: '#1A5276' },
  driver: { label: 'Driver', color: '#1E8449' },
};

function SidebarContent({ user, onLogout, unreadCount }) {
  const meta = ROLE_META[user?.role] || {
    label: "User",
    emoji: "U",
    color: "#555",
  };
  const navItems = ROLE_NAV[user?.role] || [];
  const sectionLabel = user?.role === "admin" ? "Admin" : "Account";
  const initials = user?.email?.slice(0, 2).toUpperCase() ?? "??";

  return (
    <Box
      sx={{ display: "flex", flexDirection: "column", height: "100%", p: 2.5 }}
    >
      <Typography
        sx={{
          fontFamily: '"Playfair Display", serif',
          fontSize: "1.3rem",
          fontWeight: 700,
          color: "#C0392B",
          mb: 3,
        }}
      >
        Chow
      </Typography>

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          p: 1.5,
          borderRadius: 3,
          bgcolor: "rgba(192,57,43,0.05)",
          border: "1px solid rgba(192,57,43,0.1)",
          mb: 2.5,
        }}
      >
        <Avatar
          sx={{
            width: 38,
            height: 38,
            bgcolor: meta.color,
            fontSize: "0.85rem",
            fontWeight: 700,
          }}
        >
          {initials}
        </Avatar>
        <Box sx={{ minWidth: 0 }}>
          <Typography
            variant="body2"
            fontWeight={600}
            noWrap
            sx={{ maxWidth: 130 }}
          >
            {user?.email}
          </Typography>
          <Chip
            label={meta.label}
            size="small"
            sx={{
              height: 18,
              fontSize: "0.65rem",
              bgcolor: `${meta.color}18`,
              color: meta.color,
              fontWeight: 600,
              border: "none",
            }}
          />
        </Box>
      </Box>

      <Divider sx={{ mb: 1.5 }} />

      <Typography
        variant="caption"
        color="text.secondary"
        sx={{
          px: 1,
          mb: 0.5,
          fontWeight: 600,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
        }}
      >
        {sectionLabel}
      </Typography>

      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end
          style={{ textDecoration: "none" }}
        >
          {({ isActive }) => (
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1.5,
                px: 1.5,
                py: 1,
                borderRadius: 2,
                mb: 0.5,
                bgcolor: isActive ? "rgba(192,57,43,0.08)" : "transparent",
                color: isActive ? "#C0392B" : "text.secondary",
                fontFamily: '"Lora", serif',
                fontSize: "0.875rem",
                fontWeight: isActive ? 600 : 400,
                transition: "all 0.15s",
                "&:hover": {
                  bgcolor: "rgba(192,57,43,0.05)",
                  color: "#C0392B",
                },
              }}
            >
              {item.icon}
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', gap: 1, minWidth: 0 }}>
                <Box sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {item.label}
                </Box>
                {item.to === '/notifications' && unreadCount > 0 && (
                  <Chip
                    label={unreadCount > 99 ? '99+' : unreadCount}
                    size="small"
                    sx={{
                      height: 18,
                      fontSize: '0.65rem',
                      bgcolor: isActive ? 'rgba(192,57,43,0.12)' : 'rgba(192,57,43,0.08)',
                      color: '#C0392B',
                      fontWeight: 700,
                      border: 'none',
                      flexShrink: 0,
                    }}
                  />
                )}
              </Box>
            </Box>
          )}
        </NavLink>
      ))}

      <Box sx={{ flex: 1 }} />
      <Divider sx={{ mb: 1.5 }} />

      <Box
        onClick={onLogout}
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          px: 1.5,
          py: 1,
          borderRadius: 2,
          color: "error.main",
          cursor: "pointer",
          fontSize: "0.875rem",
          fontFamily: '"Lora", serif',
          fontWeight: 500,
          transition: "all 0.15s",
          "&:hover": { bgcolor: "rgba(192,57,43,0.06)" },
        }}
      >
        <LogoutOutlined fontSize="small" />
        Sign out
      </Box>
    </Box>
  );
}

export default function DashboardLayout({ children, contentMaxWidth = 720 }) {
  const { user, logout } = useAuth();
  const { unreadCount } = useNotifications();
  const navigate = useNavigate();
  const muiTheme = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down("md"));
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const sidebar = <SidebarContent user={user} onLogout={handleLogout} unreadCount={unreadCount} />;

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "#F5F0EB" }}>
      {!isMobile && (
        <Box
          sx={{
            width: SIDEBAR_WIDTH,
            flexShrink: 0,
            bgcolor: "background.paper",
            borderRight: "0.5px solid",
            borderColor: "divider",
            position: "fixed",
            top: 0,
            left: 0,
            height: "100vh",
            overflowY: "auto",
          }}
        >
          {sidebar}
        </Box>
      )}

      {isMobile && (
        <Drawer
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          PaperProps={{ sx: { width: SIDEBAR_WIDTH } }}
        >
          {sidebar}
        </Drawer>
      )}

      <Box
        sx={{
          flex: 1,
          ml: isMobile ? 0 : `${SIDEBAR_WIDTH}px`,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {isMobile && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1.5,
              px: 2,
              py: 1.5,
              bgcolor: "background.paper",
              borderBottom: "0.5px solid",
              borderColor: "divider",
            }}
          >
            <IconButton size="small" onClick={() => setDrawerOpen(true)}>
              <MenuOutlined />
            </IconButton>
            <Typography
              sx={{
                fontFamily: '"Playfair Display", serif',
                fontWeight: 700,
                color: "#C0392B",
              }}
            >
              Chow
            </Typography>
          </Box>
        )}
        <Box
          sx={{
            p: { xs: 2.5, md: 4 },
            maxWidth: contentMaxWidth,
            width: "100%",
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
