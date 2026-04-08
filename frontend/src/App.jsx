import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme/theme';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/shared/ProtectedRoute';

import LoginPage          from './pages/auth/LoginPage';
import RegisterPage       from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage  from './pages/auth/ResetPasswordPage';
import MePage             from './pages/auth/MePage';

import CustomerProfilePage from './pages/profile/CustomerProfilePage';
import DriverProfilePage   from './pages/profile/DriverProfilePage';
import ManagerProfilePage  from './pages/profile/ManagerProfilePage';

import CartPage from './pages/cart/CartPage';
import CheckoutPage from './pages/cart/CheckoutPage';

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/"                element={<Navigate to="/login" replace />} />
            <Route path="/login"           element={<LoginPage />} />
            <Route path="/register"        element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password"  element={<ResetPasswordPage />} />

            <Route element={<ProtectedRoute />}>
              <Route path="/me" element={<MePage />} />
            </Route>

            <Route element={<ProtectedRoute roles={['customer']} />}>
              <Route path="/profile/customer" element={<CustomerProfilePage />} />
              <Route path="/cart/:restaurantId" element={<CartPage />} />
              <Route path="/checkout/:restaurantId" element={<CheckoutPage />} />
            </Route>

            <Route element={<ProtectedRoute roles={['driver']} />}>
              <Route path="/profile/driver" element={<DriverProfilePage />} />
            </Route>

            <Route element={<ProtectedRoute roles={['manager']} />}>
              <Route path="/profile/manager" element={<ManagerProfilePage />} />
            </Route>

            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}