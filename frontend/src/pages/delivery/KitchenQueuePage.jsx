import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Stack,
  Card,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from "@mui/material";
import {
  RestaurantOutlined,
  AssignmentOutlined,
  CheckCircleOutline,
  LocalShippingOutlined,
} from "@mui/icons-material";
import DashboardLayout from "../../components/shared/DashboardLayout";
import { deliveryApi } from "../../api/delivery";
import { useRestaurant } from "../../context/RestaurantContext";
import { useAuth } from "../../context/AuthContext";

function OrderCard({ order, onAssignDriver, onCancelOrder, loading }) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState("");
  const [drivers, setDrivers] = useState([]);
  const [driversLoading, setDriversLoading] = useState(false);

  const loadDrivers = async () => {
    setDriversLoading(true);
    try {
      const userApi = await import("../../api/user").then((m) => m.userApi);
      const response = await userApi.getDriversByDeliveryMethod(
        order.delivery_method,
      );
      setDrivers(response.data || []);
    } catch (err) {
      console.error("Failed to load drivers:", err);
      setDrivers([]);
    } finally {
      setDriversLoading(false);
    }
  };

  useEffect(() => {
    if (dialogOpen) {
      loadDrivers();
    }
  }, [dialogOpen]);

  const handleAssign = async () => {
    if (selectedDriver) {
      await onAssignDriver(
        order.order_id,
        selectedDriver,
        order.delivery_method,
      );
      setDialogOpen(false);
      setSelectedDriver("");
    }
  };

  return (
    <>
      <Card
        sx={{
          p: 2.5,
          borderRadius: 2,
          border: "1px solid",
          borderColor: "divider",
        }}
      >
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "start",
            mb: 2,
          }}
        >
          <Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontSize: "0.75rem", mb: 0.5 }}
            >
              Order ID: {order.order_id}
            </Typography>
            <Typography variant="h6" fontWeight={600}>
              Ready for Delivery
            </Typography>
          </Box>
          <Chip
            label="🍳 Cooking"
            color="warning"
            size="small"
            variant="outlined"
          />
        </Box>

        <Box sx={{ py: 1.5, borderY: "0.5px solid", borderColor: "divider" }}>
          <Typography variant="caption" color="text.secondary">
            Items
          </Typography>
          <Typography variant="body2" fontWeight={500}>
            {order.items?.length || 0} item
            {order.items?.length !== 1 ? "s" : ""}
          </Typography>
        </Box>

        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Delivery Address
          </Typography>
          <Typography variant="body2">{order.delivery_address}</Typography>
        </Box>

        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Total
          </Typography>
          <Typography variant="body2" fontWeight={600}>
            ${(parseInt(order.total) / 100).toFixed(2)}
          </Typography>
        </Box>

        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Delivery Method
          </Typography>
          <Chip
            label={
              order.delivery_method
                ? order.delivery_method.charAt(0).toUpperCase() +
                  order.delivery_method.slice(1)
                : "N/A"
            }
            size="small"
            variant="outlined"
            sx={{ mt: 0.5 }}
          />
        </Box>

        {!order.driver_id && (
          <Box sx={{ display: "flex", gap: 1, mt: 2 }}>
            <Button
              variant="contained"
              fullWidth
              size="small"
              startIcon={<LocalShippingOutlined />}
              onClick={() => setDialogOpen(true)}
              disabled={loading}
            >
              Assign Driver
            </Button>
            <Button
              variant="outlined"
              color="error"
              size="small"
              onClick={() => onCancelOrder(order.order_id)}
              disabled={loading}
            >
              Cancel
            </Button>
          </Box>
        )}
      </Card>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Assign Driver to Order</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1 }}>
              Delivery Method Required:{" "}
              {order.delivery_method?.toUpperCase() || "N/A"}
            </Typography>
            {driversLoading ? (
              <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
                <CircularProgress size={24} />
              </Box>
            ) : drivers.length > 0 ? (
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Select Driver</InputLabel>
                <Select
                  value={selectedDriver}
                  label="Select Driver"
                  onChange={(e) => setSelectedDriver(e.target.value)}
                >
                  {drivers.map((driver) => (
                    <MenuItem key={driver.user_id} value={driver.user_id}>
                      {driver.name} ({driver.delivery_method})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                No drivers available with {order.delivery_method} delivery
                method.
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAssign}
            variant="contained"
            disabled={!selectedDriver || driversLoading}
          >
            Assign
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default function KitchenQueuePage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [restaurant, setRestaurant] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const fetchKitchenQueue = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      // First, get the restaurant owned by the manager
      const restaurantData = await import("../../api/restaurant").then((m) =>
        m.restaurantApi.getAll(),
      );
      const owned = restaurantData.data.find(
        (r) => String(r.owner_id) === String(user?.user_id),
      );

      if (owned) {
        setRestaurant(owned);
        const queueResponse = await deliveryApi.getKitchenQueue(owned.id);
        setOrders(queueResponse.data || []);
      }
    } catch (err) {
      setFeedback({
        type: "error",
        message: err.response?.data?.detail || "Failed to load kitchen queue",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKitchenQueue();
  }, [user?.user_id]);

  const handleAssignDriver = async (orderId, driverId, deliveryMethod) => {
    setAssigning(true);
    setFeedback(null);
    try {
      await deliveryApi.assignDriver(orderId, driverId, deliveryMethod);
      setFeedback({ type: "success", message: "Driver assigned successfully" });
      await fetchKitchenQueue();
    } catch (err) {
      setFeedback({
        type: "error",
        message: err.response?.data?.detail || "Failed to assign driver",
      });
    } finally {
      setAssigning(false);
    }
  };

  const handleCancelOrder = async (orderId) => {
    setAssigning(true);
    setFeedback(null);
    try {
      await deliveryApi.cancelOrder(orderId);
      setFeedback({ type: "success", message: "Order cancelled successfully" });
      await fetchKitchenQueue();
    } catch (err) {
      setFeedback({
        type: "error",
        message: err.response?.data?.detail || "Failed to cancel order",
      });
    } finally {
      setAssigning(false);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ maxWidth: 900, mx: "auto", px: 3, py: 4 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 3 }}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 2.5,
              bgcolor: "rgba(192,57,43,0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <RestaurantOutlined sx={{ color: "#C0392B", fontSize: 22 }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" sx={{ fontSize: "1.4rem" }}>
              {restaurant?.name || "Kitchen"} Queue
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {orders.length} order{orders.length !== 1 ? "s" : ""} ready for
              delivery
            </Typography>
          </Box>
          <Button
            variant="outlined"
            size="small"
            onClick={fetchKitchenQueue}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {feedback && (
          <Alert severity={feedback.type} sx={{ mb: 2 }}>
            {feedback.message}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
            <CircularProgress />
          </Box>
        ) : orders.length === 0 ? (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <CheckCircleOutline
              sx={{ fontSize: 48, color: "text.disabled", mb: 1 }}
            />
            <Typography color="text.secondary">
              No orders ready for delivery
            </Typography>
          </Box>
        ) : (
          <Stack spacing={2}>
            {orders.map((order) => (
              <OrderCard
                key={order.order_id}
                order={order}
                onAssignDriver={handleAssignDriver}
                onCancelOrder={handleCancelOrder}
                loading={assigning}
              />
            ))}
          </Stack>
        )}
      </Box>
    </DashboardLayout>
  );
}
