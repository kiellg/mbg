import { useEffect, useState } from 'react';
import {
  Box, Typography, Card, CardContent, CardActions,
  Chip, Stack, Button, Divider, CircularProgress,
  Alert, Collapse
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import DashboardLayout from '../../components/shared/DashboardLayout';
import ReviewDialog from '../../components/orders/ReviewDialog';
import { ordersApi } from '../../api/orders';

const STATUS_COLOR = {
  'Pending':          'warning',
  'Cooking':          'info',
  'Out for Delivery': 'primary',
  'Delivered':        'success',
  'Cancelled':        'error',
};

const DELIVERY_ICON = { walk: '🚶', bike: '🚲', car: '🚗' };

export default function OrdersPage() {
  const [orders, setOrders]           = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);
  const [expanded, setExpanded]       = useState({});  // { [order_id]: bool }
  const [reviewed, setReviewed]       = useState({});  // { [order_id]: bool }
  const [reviewTarget, setReviewTarget] = useState(null);

  useEffect(() => {
    ordersApi.getAll()
      .then(({ data }) => {
        setOrders([...data].sort((a, b) =>
          new Date(b.created_at) - new Date(a.created_at)
        ));
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load orders'))
      .finally(() => setLoading(false));
  }, []);

  const toggleExpand = (id) =>
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  const handleReviewed = (orderId) =>
    setReviewed((prev) => ({ ...prev, [orderId]: true }));

  if (loading) return (
    <DashboardLayout>
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    </DashboardLayout>
  );

  return (
    <DashboardLayout>
      <Typography variant="h4" fontWeight={700} sx={{ mb: 1 }}>My Orders</Typography>
      <Box sx={{ height: 4, width: 48,
        background: 'linear-gradient(90deg, #C0392B, #E74C3C)',
        borderRadius: 2, mb: 4 }} />

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {!loading && orders.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">No orders yet</Typography>
          <Typography variant="body2" color="text.secondary">
            Place your first order to see it here.
          </Typography>
        </Box>
      )}

      <Stack spacing={2}>
        {orders.map((order) => (
          <Card key={order.order_id} variant="outlined">
            <CardContent sx={{ pb: 1 }}>

              {/* Header */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between',
                alignItems: 'flex-start', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                <Box>
                  <Typography variant="body1" fontWeight={700}>
                    Order #{order.order_id}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(order.created_at).toLocaleString()} ·{' '}
                    {DELIVERY_ICON[order.delivery_method]} {order.delivery_method}
                  </Typography>
                </Box>
                <Chip
                  label={order.status}
                  color={STATUS_COLOR[order.status] ?? 'default'}
                  size="small"
                />
              </Box>

              {/* Items list */}
              <Stack spacing={0.25} sx={{ mb: 1 }}>
                {order.items.map((item, idx) => (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }} key={idx}>
                    <Typography variant="body2" color="text.secondary">
                      {item.quantity}× {item.item_name}
                    </Typography>
                    <Typography variant="body2">${parseFloat(item.item_price).toFixed(2)}</Typography>
                  </Box>
                ))}
              </Stack>

              {/* Expandable cost breakdown */}
              <Collapse in={!!expanded[order.order_id]}>
                <Divider sx={{ my: 1.5, borderColor: '#EDE5D8' }} />
                <Stack spacing={0.75} sx={{ mb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Subtotal</Typography>
                    <Typography variant="body2">${parseFloat(order.subtotal).toFixed(2)}</Typography>
                  </Box>
                  {parseFloat(order.discount) > 0 && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="success.main">
                        Discount {order.coupon_code ? `(${order.coupon_code})` : ''}
                      </Typography>
                      <Typography variant="body2" color="success.main">
                        -${parseFloat(order.discount).toFixed(2)}
                      </Typography>
                    </Box>
                  )}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Tax</Typography>
                    <Typography variant="body2">${parseFloat(order.tax).toFixed(2)}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Delivery fee</Typography>
                    <Typography variant="body2">${parseFloat(order.delivery_fee).toFixed(2)}</Typography>
                  </Box>
                  <Divider sx={{ borderColor: '#EDE5D8' }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" fontWeight={700}>Total</Typography>
                    <Typography variant="body2" fontWeight={700} color="primary">
                      ${parseFloat(order.total).toFixed(2)}
                    </Typography>
                  </Box>
                </Stack>
                <Typography variant="caption" color="text.secondary">
                  Delivered to: {order.delivery_address}
                </Typography>
              </Collapse>

            </CardContent>

            <CardActions sx={{ px: 2, pt: 0, pb: 1.5,
              display: 'flex', justifyContent: 'space-between' }}>
              <Button size="small" color="inherit"
                endIcon={expanded[order.order_id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                onClick={() => toggleExpand(order.order_id)}>
                {expanded[order.order_id] ? 'Hide details' : 'View breakdown'}
              </Button>

              {/* Review button — only on Delivered, only if not yet reviewed */}
              {order.status === 'Delivered' && !reviewed[order.order_id] && (
                <Button size="small" variant="outlined" color="primary"
                  startIcon={<StarBorderIcon />}
                  onClick={() => setReviewTarget(order)}>
                  Leave a Review
                </Button>
              )}
              {order.status === 'Delivered' && reviewed[order.order_id] && (
                <Typography variant="caption" color="success.main" fontWeight={600}>
                  ✓ Review submitted
                </Typography>
              )}
            </CardActions>
          </Card>
        ))}
      </Stack>

      {/* Review dialog */}
      <ReviewDialog
        open={!!reviewTarget}
        order={reviewTarget}
        onClose={() => setReviewTarget(null)}
        onReviewed={handleReviewed}
      />
    </DashboardLayout>
  );
}