import { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Rating, TextField, Typography, Box, Alert, CircularProgress
} from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import { reviewsApi } from '../../api/reviews';

export default function ReviewDialog({ open, onClose, order, onReviewed }) {
  const [rating, setRating]   = useState(0);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [done, setDone]       = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) { setError('Please select a star rating.'); return; }
    setLoading(true); setError(null);
    try {
      await reviewsApi.submit({
        order_id: order.order_id,
        rating,
        comment: comment.trim() || null,
      });
      setDone(true);
      onReviewed(order.order_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit review. Try again.');
    } finally { setLoading(false); }
  };

  const handleClose = () => {
    setRating(0); setComment(''); setError(null); setDone(false);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>
        {done ? 'Thanks for your review!' : `Review your order`}
      </DialogTitle>
      <DialogContent>
        {done ? (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <StarIcon sx={{ fontSize: 56, color: '#f59e0b' }} />
            <Typography variant="body1" sx={{ mt: 1 }}>
              Your feedback helps other customers.
            </Typography>
          </Box>
        ) : (
          <Box sx={{ pt: 1 }}>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Order #{order?.order_id} · How was your experience?
            </Typography>
            <Rating
              size="large"
              value={rating}
              onChange={(_, v) => setRating(v)}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth multiline rows={3}
              label="Write a comment (optional)"
              placeholder="Tell others about the food and service..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              inputProps={{ maxLength: 500 }}
            />
            <Typography variant="caption" color="text.secondary">
              {comment.length}/500
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} color="inherit">
          {done ? 'Close' : 'Cancel'}
        </Button>
        {!done && (
          <Button variant="contained" color="primary"
            disabled={loading} onClick={handleSubmit}>
            {loading ? <CircularProgress size={20} color="inherit" /> : 'Submit Review'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}