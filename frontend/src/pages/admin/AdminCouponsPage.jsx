import { useEffect, useMemo, useState } from 'react';
import {
  Alert, Box, Button, Chip, CircularProgress, FormControl,
  FormControlLabel, InputLabel, MenuItem, Paper, Select,
  Stack, Switch, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, TextField, Typography,
} from '@mui/material';
import DashboardLayout from '../../components/shared/DashboardLayout';
import { adminApi } from '../../api/admin';

const EMPTY_FORM = {
  code: '',
  discount_type: 'percentage',
  percent_off: '',
  amount_off_cents: '',
  minimum_subtotal_cents: '0',
  expires_at: '',
  is_active: true,
};

function getApiError(error, fallback = 'Request failed') {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || fallback).join(', ');
  }

  return detail || fallback;
}

function toFormState(coupon) {
  return {
    code: coupon.code || '',
    discount_type: coupon.discount_type || 'percentage',
    percent_off: coupon.percent_off != null ? String(coupon.percent_off) : '',
    amount_off_cents: coupon.amount_off_cents != null ? String(coupon.amount_off_cents) : '',
    minimum_subtotal_cents: String(coupon.minimum_subtotal_cents ?? 0),
    expires_at: coupon.expires_at ? new Date(coupon.expires_at).toISOString().slice(0, 16) : '',
    is_active: coupon.is_active ?? true,
  };
}

function formatCurrencyFromCents(cents) {
  return `$${((cents || 0) / 100).toFixed(2)}`;
}

function validateForm(form, isEditing) {
  if (!isEditing && !form.code.trim()) {
    return 'Coupon code is required.';
  }

  if (!/^\d+$/.test(form.minimum_subtotal_cents.trim())) {
    return 'Minimum subtotal must be a whole number of cents.';
  }

  if (form.discount_type === 'percentage') {
    const percent = Number(form.percent_off);
    if (!Number.isInteger(percent) || percent <= 0 || percent > 100) {
      return 'Percent off must be a whole number between 1 and 100.';
    }
    return null;
  }

  const amount = Number(form.amount_off_cents);
  if (!Number.isInteger(amount) || amount <= 0) {
    return 'Amount off must be a positive whole number of cents.';
  }

  return null;
}

function buildPayload(form, isEditing) {
  const payload = {
    discount_type: form.discount_type,
    percent_off: form.discount_type === 'percentage' ? Number(form.percent_off) : null,
    amount_off_cents: form.discount_type === 'fixed_amount' ? Number(form.amount_off_cents) : null,
    minimum_subtotal_cents: Number(form.minimum_subtotal_cents || 0),
    expires_at: form.expires_at ? new Date(form.expires_at).toISOString() : null,
    is_active: form.is_active,
  };

  if (!isEditing) {
    payload.code = form.code.trim().toUpperCase();
  }

  return payload;
}

function requireArray(data, label) {
  if (Array.isArray(data)) {
    return data;
  }

  throw new Error(`Unexpected ${label} response format.`);
}

export default function AdminCouponsPage() {
  const [coupons, setCoupons] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [actionCode, setActionCode] = useState(null);
  const [editingCode, setEditingCode] = useState(null);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const isEditing = Boolean(editingCode);

  const sortedCoupons = useMemo(
    () => [...coupons].sort((left, right) => left.code.localeCompare(right.code)),
    [coupons],
  );

  useEffect(() => {
    let active = true;

    const loadCoupons = async () => {
      setLoading(true);
      setError(null);

      try {
        const { data } = await adminApi.listCoupons();
        if (!active) {
          return;
        }

        setCoupons(requireArray(data, 'coupons'));
      } catch (err) {
        if (!active) {
          return;
        }

        setError(getApiError(err, 'Failed to load coupons'));
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadCoupons();
    return () => {
      active = false;
    };
  }, []);

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingCode(null);
  };

  const refreshCoupons = async () => {
    const { data } = await adminApi.listCoupons();
    setCoupons(requireArray(data, 'coupons'));
  };

  const handleFieldChange = (field) => (event) => {
    const value = field === 'is_active' ? event.target.checked : event.target.value;
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  };

  const handleDiscountTypeChange = (event) => {
    const nextType = event.target.value;
    setForm((currentForm) => ({
      ...currentForm,
      discount_type: nextType,
      percent_off: nextType === 'percentage' ? currentForm.percent_off : '',
      amount_off_cents: nextType === 'fixed_amount' ? currentForm.amount_off_cents : '',
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFeedback(null);
    setError(null);

    const validationError = validateForm(form, isEditing);
    if (validationError) {
      setError(validationError);
      return;
    }

    setSaving(true);

    try {
      const payload = buildPayload(form, isEditing);
      if (isEditing) {
        await adminApi.updateCoupon(editingCode, payload);
        setFeedback({ type: 'success', message: `Updated ${editingCode}.` });
      } else {
        await adminApi.createCoupon(payload);
        setFeedback({ type: 'success', message: `Created ${payload.code}.` });
      }

      await refreshCoupons();
      resetForm();
    } catch (err) {
      setError(getApiError(err, 'Failed to save coupon'));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (coupon) => {
    setFeedback(null);
    setError(null);
    setEditingCode(coupon.code);
    setForm(toFormState(coupon));
  };

  const handleDeactivate = async (coupon) => {
    if (!coupon.is_active) {
      return;
    }

    setActionCode(coupon.code);
    setFeedback(null);
    setError(null);

    try {
      await adminApi.deactivateCoupon(coupon.code);
      await refreshCoupons();
      setFeedback({ type: 'success', message: `Deactivated ${coupon.code}.` });
      if (editingCode === coupon.code) {
        setForm((currentForm) => ({ ...currentForm, is_active: false }));
      }
    } catch (err) {
      setError(getApiError(err, 'Failed to deactivate coupon'));
    } finally {
      setActionCode(null);
    }
  };

  const handleDelete = async (coupon) => {
    const confirmed = window.confirm(`Delete coupon ${coupon.code}?`);
    if (!confirmed) {
      return;
    }

    setActionCode(coupon.code);
    setFeedback(null);
    setError(null);

    try {
      await adminApi.deleteCoupon(coupon.code);
      setCoupons((currentCoupons) => currentCoupons.filter((currentCoupon) => currentCoupon.code !== coupon.code));
      setFeedback({ type: 'success', message: `Deleted ${coupon.code}.` });
      if (editingCode === coupon.code) {
        resetForm();
      }
    } catch (err) {
      setError(getApiError(err, 'Failed to delete coupon'));
    } finally {
      setActionCode(null);
    }
  };

  return (
    <DashboardLayout contentMaxWidth={1180}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontFamily: '"Playfair Display", serif', mb: 0.5 }}>
            Coupon management
          </Typography>
          <Typography color="text.secondary">
            Create, edit, deactivate, and delete discount codes.
          </Typography>
        </Box>

        {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}
        {error && <Alert severity="error">{error}</Alert>}

        <Paper elevation={0} sx={{ p: 2.5, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" sx={{ mb: 2, fontFamily: '"Playfair Display", serif' }}>
            {isEditing ? `Edit ${editingCode}` : 'Create coupon'}
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, minmax(0, 1fr))', xl: 'repeat(3, minmax(0, 1fr))' }, gap: 2 }}>
              <TextField
                label="Coupon code"
                value={form.code}
                onChange={handleFieldChange('code')}
                disabled={isEditing}
                placeholder="SAVE10"
              />

              <FormControl fullWidth>
                <InputLabel id="discount-type-label">Discount type</InputLabel>
                <Select
                  labelId="discount-type-label"
                  label="Discount type"
                  value={form.discount_type}
                  onChange={handleDiscountTypeChange}
                >
                  <MenuItem value="percentage">Percentage</MenuItem>
                  <MenuItem value="fixed_amount">Fixed amount</MenuItem>
                </Select>
              </FormControl>

              {form.discount_type === 'percentage' ? (
                <TextField
                  label="Percent off"
                  type="number"
                  inputProps={{ min: 1, max: 100, step: 1 }}
                  value={form.percent_off}
                  onChange={handleFieldChange('percent_off')}
                />
              ) : (
                <TextField
                  label="Amount off (cents)"
                  type="number"
                  inputProps={{ min: 1, step: 1 }}
                  value={form.amount_off_cents}
                  onChange={handleFieldChange('amount_off_cents')}
                />
              )}

              <TextField
                label="Minimum subtotal (cents)"
                type="number"
                inputProps={{ min: 0, step: 1 }}
                value={form.minimum_subtotal_cents}
                onChange={handleFieldChange('minimum_subtotal_cents')}
              />

              <TextField
                label="Expires at"
                type="datetime-local"
                value={form.expires_at}
                onChange={handleFieldChange('expires_at')}
                InputLabelProps={{ shrink: true }}
              />

              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <FormControlLabel
                  control={<Switch checked={form.is_active} onChange={handleFieldChange('is_active')} />}
                  label="Active"
                />
              </Box>
            </Box>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
              <Button type="submit" variant="contained" disabled={saving}>
                {saving ? 'Saving...' : isEditing ? 'Update coupon' : 'Create coupon'}
              </Button>
              <Button type="button" variant="outlined" onClick={resetForm} disabled={saving}>
                {isEditing ? 'Cancel edit' : 'Clear form'}
              </Button>
            </Stack>
          </Box>
        </Paper>

        {loading ? (
          <Paper elevation={0} sx={{ p: 4, borderRadius: 3, display: 'flex', justifyContent: 'center' }}>
            <CircularProgress />
          </Paper>
        ) : (
          <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Code</TableCell>
                  <TableCell>Discount</TableCell>
                  <TableCell>Minimum subtotal</TableCell>
                  <TableCell>Expires</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sortedCoupons.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6}>
                      <Typography color="text.secondary">No coupons found.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  sortedCoupons.map((coupon) => {
                    const isBusy = actionCode === coupon.code;

                    return (
                      <TableRow key={coupon.code} hover>
                        <TableCell>{coupon.code}</TableCell>
                        <TableCell>
                          {coupon.discount_type === 'percentage'
                            ? `${coupon.percent_off}% off`
                            : `${formatCurrencyFromCents(coupon.amount_off_cents)} off`}
                        </TableCell>
                        <TableCell>{formatCurrencyFromCents(coupon.minimum_subtotal_cents)}</TableCell>
                        <TableCell>
                          {coupon.expires_at ? new Date(coupon.expires_at).toLocaleString() : 'No expiry'}
                        </TableCell>
                        <TableCell>
                          <Chip label={coupon.is_active ? 'Active' : 'Inactive'} color={coupon.is_active ? 'success' : 'default'} size="small" />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} justifyContent="flex-end">
                            <Button size="small" onClick={() => handleEdit(coupon)}>
                              Edit
                            </Button>
                            <Button size="small" onClick={() => handleDeactivate(coupon)} disabled={!coupon.is_active || isBusy}>
                              {isBusy ? 'Working...' : 'Deactivate'}
                            </Button>
                            <Button size="small" color="error" onClick={() => handleDelete(coupon)} disabled={isBusy}>
                              Delete
                            </Button>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </DashboardLayout>
  );
}
