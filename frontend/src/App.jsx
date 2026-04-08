import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme/theme';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { RestaurantProvider } from './context/RestaurantContext';
import ProtectedRoute from './components/shared/ProtectedRoute';

import LoginPage          from './pages/auth/LoginPage';
import RegisterPage       from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage  from './pages/auth/ResetPasswordPage';
import MePage             from './pages/auth/MePage';

import CustomerProfilePage from './pages/profile/CustomerProfilePage';
import DriverProfilePage   from './pages/profile/DriverProfilePage';
import ManagerProfilePage  from './pages/profile/ManagerProfilePage';
import AdminDashboardPage  from './pages/admin/AdminDashboardPage';
import AdminUsersPage      from './pages/admin/AdminUsersPage';
import AdminCouponsPage    from './pages/admin/AdminCouponsPage';

import RestaurantListPage   from './pages/restaurant/RestaurantListPage';
import RestaurantDetailPage from './pages/restaurant/RestaurantDetailPage';
import ManageRestaurantPage from './pages/restaurant/manager/ManageRestaurantPage';
import ManageMenuPage       from './pages/restaurant/manager/ManageMenuPage';
import FavouritesPage       from './pages/FavouritesPage';

import CartPage     from './pages/cart/CartPage';
import CheckoutPage from './pages/cart/CheckoutPage';
import PaymentPage  from './pages/payment/PaymentPage';
import OrdersPage from './pages/orders/OrdersPage';

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <RestaurantProvider>
          <CartProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Navigate to="/login" replace />} />
                <Route path="/login"           element={<LoginPage />} />
                <Route path="/register"        element={<RegisterPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password"  element={<ResetPasswordPage />} />

                {/* Any logged-in user */}
                <Route element={<ProtectedRoute />}>
                  <Route path="/me"                  element={<MePage />} />
                  <Route path="/restaurants"         element={<RestaurantListPage />} />
                  <Route path="/restaurants/:id"     element={<RestaurantDetailPage />} />
                  <Route path="/favourites"          element={<FavouritesPage />} />
                </Route>

                {/* Customer only */}
                <Route element={<ProtectedRoute roles={['customer']} />}>
                  <Route path="/profile/customer"      element={<CustomerProfilePage />} />
                  <Route path="/cart/:restaurantId"     element={<CartPage />} />
                  <Route path="/checkout/:restaurantId" element={<CheckoutPage />} />
                  <Route path="/payment/:orderId"       element={<PaymentPage />} />
                  <Route path="/orders" element={<OrdersPage />} />
                </Route>

                {/* Driver only */}
                <Route element={<ProtectedRoute roles={['driver']} />}>
                  <Route path="/profile/driver" element={<DriverProfilePage />} />
                </Route>

                {/* Manager only */}
                <Route element={<ProtectedRoute roles={['manager']} />}>
                  <Route path="/profile/manager"   element={<ManagerProfilePage />} />
                  <Route path="/manage/restaurant" element={<ManageRestaurantPage />} />
                  <Route path="/manage/menu"       element={<ManageMenuPage />} />
                </Route>

                {/* Admin only */}
                <Route element={<ProtectedRoute roles={['admin']} />}>
                  <Route path="/admin"         element={<AdminDashboardPage />} />
                  <Route path="/admin/users"   element={<AdminUsersPage />} />
                  <Route path="/admin/coupons" element={<AdminCouponsPage />} />
                </Route>

                <Route path="*" element={<Navigate to="/login" replace />} />
              </Routes>
            </BrowserRouter>
          </CartProvider>
        </RestaurantProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}