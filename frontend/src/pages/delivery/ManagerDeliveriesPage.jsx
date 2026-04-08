import { useEffect, useState } from "react";
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Stack,
  Card,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import {
  LocalShippingOutlined,
  CheckCircleOutline,
  TimelineOutlined,
  CancelOutlined,
  MapOutlined,
} from "@mui/icons-material";
import DashboardLayout from "../../components/shared/DashboardLayout";
import { deliveryApi } from "../../api/delivery";

const STATUS_META = {
  Pending: { icon: "🕐", color: "warning", label: "Pending" },
  Cooking: { icon: "🍳", color: "info", label: "Cooking" },
  "Out for Delivery": { icon: "🚴", color: "info", label: "Out for Delivery" },
  Delivered: { icon: "✅", color: "success", label: "Delivered" },
  Cancelled: { icon: "❌", color: "error", label: "Cancelled" },
};

function ManagerDeliveryCard({ delivery, onUpdateStatus, loading }) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState(delivery.status);

  const statusMeta = STATUS_META[delivery.status] || {};
  // Manager can only cancel when order is in Cooking status
  const nextStatuses = {
    Pending: [],
    Cooking: ["Cancelled"],
    "Out for Delivery": [],
    Delivered: [],
    Cancelled: [],
  };

  const handleStatusUpdate = async () => {
    if (newStatus !== delivery.status) {
      await onUpdateStatus(delivery.order_id, newStatus);
      setDialogOpen(false);
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
          ":hover": { boxShadow: 2 },
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
              Order ID: {delivery.order_id}
            </Typography>
            <Typography variant="h6" fontWeight={600}>
              Order Management
            </Typography>
          </Box>
          <Chip
            label={statusMeta.label}
            color={statusMeta.color}
            size="small"
            variant="outlined"
          />
        </Box>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 2,
            py: 1.5,
            borderY: "0.5px solid",
            borderColor: "divider",
          }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              Delivery Method
            </Typography>
            <Typography variant="body2" fontWeight={500}>
              {delivery.delivery_method === "walk" && "🚶 Walking"}
              {delivery.delivery_method === "bike" && "🚴 Bicycle"}
              {delivery.delivery_method === "car" && "🚗 Car"}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Estimated Arrival
            </Typography>
            <Typography variant="body2" fontWeight={500}>
              {delivery.estimated_arrival || "TBD"}
            </Typography>
          </Box>
        </Box>

        <Box sx={{ mt: 2, display: "flex", gap: 1, alignItems: "center" }}>
          <MapOutlined fontSize="small" sx={{ color: "text.secondary" }} />
          <Typography variant="body2">{delivery.customer_address}</Typography>
        </Box>

        <Box sx={{ mt: 1.5, display: "flex", gap: 1, alignItems: "center" }}>
          <Typography variant="caption" color="text.secondary">
            📞
          </Typography>
          <Typography variant="body2">
            {delivery.customer_phone || "No phone provided"}
          </Typography>
        </Box>

        {nextStatuses[delivery.status]?.length > 0 && (
          <Button
            variant="contained"
            color="error"
            size="small"
            fullWidth
            sx={{ mt: 2 }}
            onClick={() => setDialogOpen(true)}
            disabled={loading}
          >
            Cancel Order
          </Button>
        )}
      </Card>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Cancel Delivery</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mt: 2 }}>
            Are you sure you want to cancel this order?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Keep Order</Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleStatusUpdate}
            disabled={loading}
          >
            {loading ? "Cancelling..." : "Cancel Order"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default function ManagerDeliveriesPage() {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [filter, setFilter] = useState("all");

  const fetchDeliveries = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      const response = await deliveryApi.getAssignedDeliveries();
      setDeliveries(response.data || []);
    } catch (err) {
      setFeedback({
        type: "error",
        message: err.response?.data?.detail || "Failed to load deliveries",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeliveries();
  }, []);

  const handleUpdateStatus = async (orderId, newStatus) => {
    setUpdating(true);
    setFeedback(null);
    try {
      await deliveryApi.updateDeliveryStatus(orderId, newStatus);
      setFeedback({
        type: "success",
        message: `Order cancelled successfully`,
      });
      await fetchDeliveries();
    } catch (err) {
      setFeedback({
        type: "error",
        message: err.response?.data?.detail || "Failed to cancel order",
      });
    } finally {
      setUpdating(false);
    }
  };

  const filteredDeliveries =
    filter === "all"
      ? deliveries
      : deliveries.filter((d) => d.status === filter);

  const cookingCount = deliveries.filter((d) => d.status === "Cooking").length;

  return (
    <DashboardLayout>
      <Box sx={{ maxWidth: 900, mx: "auto", px: 3, py: 4 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 3 }}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 2.5,
              bgcolor: "rgba(26,82,118,0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <CancelOutlined sx={{ color: "#1A5276", fontSize: 22 }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" sx={{ fontSize: "1.4rem" }}>
              Order Management
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {cookingCount} order{cookingCount !== 1 ? "s" : ""} available to
              cancel
            </Typography>
          </Box>
        </Box>

        {feedback && (
          <Alert severity={feedback.type} sx={{ mb: 2 }}>
            {feedback.message}
          </Alert>
        )}

        <Box sx={{ display: "flex", gap: 1, mb: 3, overflowX: "auto" }}>
          {[
            { value: "all", label: "All" },
            { value: "Cooking", label: "Cooking" },
            { value: "Out for Delivery", label: "Out for Delivery" },
            { value: "Delivered", label: "Delivered" },
            { value: "Cancelled", label: "Cancelled" },
          ].map(({ value, label }) => (
            <Button
              key={value}
              variant={filter === value ? "contained" : "outlined"}
              size="small"
              onClick={() => setFilter(value)}
            >
              {label}
            </Button>
          ))}
        </Box>

        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
            <CircularProgress />
          </Box>
        ) : filteredDeliveries.length === 0 ? (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <LocalShippingOutlined
              sx={{ fontSize: 48, color: "text.disabled", mb: 1 }}
            />
            <Typography color="text.secondary">
              {filter === "all"
                ? "No deliveries found"
                : `No "${filter}" deliveries`}
            </Typography>
          </Box>
        ) : (
          <Stack spacing={2}>
            {filteredDeliveries.map((delivery) => (
              <ManagerDeliveryCard
                key={delivery.order_id}
                delivery={delivery}
                onUpdateStatus={handleUpdateStatus}
                loading={updating}
              />
            ))}
          </Stack>
        )}
      </Box>
    </DashboardLayout>
  );
}
