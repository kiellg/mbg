import { useNavigate, Navigate } from "react-router-dom";
import {
  Box,
  Button,
  Typography,
  Paper,
  Chip,
  Avatar,
  Divider,
} from "@mui/material";
import {
  EmailOutlined,
  FingerprintOutlined,
  BadgeOutlined,
  LogoutOutlined,
} from "@mui/icons-material";
import AuthLayout from "../../components/shared/AuthLayout";
import { useAuth } from "../../context/AuthContext";

const ROLE_META = {
  admin:    { label: 'Admin',    emoji: 'A', color: 'secondary' },
  customer: { label: 'Customer', emoji: 'C', color: 'warning' },
  manager:  { label: 'Manager',  emoji: 'M', color: 'info'    },
  driver:   { label: 'Driver',   emoji: 'D', color: 'success' },
};

function InfoRow({ icon: Icon, label, value }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, py: 1.25 }}>
      <Icon sx={{ fontSize: 18, color: "text.secondary", flexShrink: 0 }} />
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography variant="caption" color="text.secondary" display="block">{label}</Typography>
        <Typography variant="body2" fontWeight={500} sx={{ wordBreak: 'break-all' }}>{value ?? '--'}</Typography>
      </Box>
    </Box>
  );
}

export default function MePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    return (
      <AuthLayout
        title="Not signed in"
        subtitle="Please log in to view your profile"
      >
        <Button
          variant="contained"
          fullWidth
          onClick={() => navigate("/login")}
        >
          Go to login
        </Button>
      </AuthLayout>
    );
  }

  const roleRoute = {
    customer: "/profile/customer",
    manager: "/manager/restaurant",
    driver: "/profile/driver",
  };
  const roleRoute = { admin: '/admin', customer: '/profile/customer', manager: '/profile/manager', driver: '/profile/driver' };
  if (user.role && roleRoute[user.role]) {
    return <Navigate to={roleRoute[user.role]} replace />;
  }

  const meta = ROLE_META[user.role] || { label: user.role, emoji: 'U', color: 'default' };
  const initials = user.email?.slice(0, 2).toUpperCase() ?? '??';
  const handleLogout = async () => { await logout(); navigate('/login'); };

  return (
    <AuthLayout title="My profile" subtitle="Your current session">
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <Paper
          elevation={0}
          sx={{
            p: 2.5,
            display: "flex",
            alignItems: "center",
            gap: 2,
            borderRadius: 3,
            bgcolor: "rgba(192,57,43,0.05)",
            border: "1px solid rgba(192,57,43,0.12)",
          }}
        >
          <Avatar
            sx={{
              width: 52,
              height: 52,
              bgcolor: "primary.main",
              fontFamily: '"Playfair Display", serif',
              fontSize: "1.1rem",
              fontWeight: 700,
            }}
          >
            {initials}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body1" fontWeight={600} noWrap>
              {user.email}
            </Typography>
            <Chip
              label={`${meta.emoji}  ${meta.label}`}
              size="small"
              color={meta.color}
              variant="outlined"
              sx={{ mt: 0.5, fontSize: "0.75rem", height: 22 }}
            />
          </Box>
        </Paper>

        <Paper
          elevation={0}
          sx={{
            px: 2,
            py: 0.5,
            border: "0.5px solid",
            borderColor: "divider",
            borderRadius: 3,
          }}
        >
          <InfoRow
            icon={FingerprintOutlined}
            label="User ID"
            value={user.user_id}
          />
          <Divider />
          <InfoRow icon={EmailOutlined} label="Email" value={user.email} />
          <Divider />
          <InfoRow icon={BadgeOutlined} label="Role" value={meta.label} />
        </Paper>

        <Button
          variant="outlined"
          color="error"
          fullWidth
          startIcon={<LogoutOutlined />}
          onClick={handleLogout}
        >
          Sign out
        </Button>
      </Box>
    </AuthLayout>
  );
}
