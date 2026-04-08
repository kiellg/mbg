import { createContext, useContext, useState, useCallback } from "react";
import { cartApi } from "../api/cart";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [cart, setCart]       = useState(null);   // { items: [], total: 0 }
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const clearError = useCallback(() => setError(null), []);

  const fetchCart = useCallback(async (restaurantId) => {
    setLoading(true); setError(null);
    try {
      const { data } = await cartApi.getCart(restaurantId);
      setCart(data);
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to load cart';
      setError(msg);
      return { success: false, message: msg };
    } finally { setLoading(false); }
  }, []);

  const addItem = useCallback(async (restaurantId, payload) => {
    setLoading(true); setError(null);
    try {
      const { data } = await cartApi.addItem(restaurantId, payload);
      setCart(data);
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to add item';
      setError(msg);
      return { success: false, message: msg };
    } finally { setLoading(false); }
  }, []);

  const updateItem = useCallback(async (restaurantId, itemId, {quantity: qty}) => {
    setLoading(true); setError(null);
    try {
      const { data } = await cartApi.updateItem(restaurantId, itemId, {quantity: qty});
      setCart(data);
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to update item';
      setError(msg);
      return { success: false, message: msg };
    } finally { setLoading(false); }
  }, []);

  const removeItem = useCallback(async (restaurantId, itemId) => {
    setLoading(true); setError(null);
    try {
      await cartApi.removeItem(restaurantId, itemId);
      await fetchCart(restaurantId);
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to remove item';
      setError(msg);
      return { success: false, message: msg };
    } finally { setLoading(false); }
  }, []);

  return (
    <CartContext.Provider value={{ cart, loading, error, clearError, fetchCart, addItem, updateItem, removeItem }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used inside CartProvider');
  return ctx;
};