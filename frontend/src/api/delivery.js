import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const axiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

export const deliveryApi = {
  /**
   * Get all deliveries assigned to the current driver
   */
  async getAssignedDeliveries() {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.get("/orders/assigned", {
      headers: { "session-token": sessionToken },
    });
  },

  /**
   * Get delivery status for an order
   */
  async getDeliveryStatus(orderId) {
    return axiosInstance.get(`/orders/${orderId}/status`);
  },

  /**
   * Get delivery details for an order
   */
  async getDeliveryDetails(orderId) {
    return axiosInstance.get(`/orders/${orderId}/details`);
  },

  /**
   * Update delivery status for an order (driver action)
   */
  async updateDeliveryStatus(orderId, newStatus) {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.patch(
      `/orders/${orderId}/status`,
      { status: newStatus },
      { headers: { "session-token": sessionToken } },
    );
  },

  /**
   * Mark order as out for delivery
   */
  async markOutForDelivery(orderId) {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.patch(
      `/orders/${orderId}/status/out-for-delivery`,
      {},
      {
        headers: { "session-token": sessionToken },
      },
    );
  },

  /**
   * Mark order as delivered
   */
  async markDelivered(orderId) {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.patch(
      `/orders/${orderId}/status/delivered`,
      {},
      {
        headers: { "session-token": sessionToken },
      },
    );
  },

  /**
   * Assign a driver to an order (manager action)
   */
  async assignDriver(orderId, driverId, deliveryMethod) {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.patch(
      `/orders/${orderId}/driver`,
      { driver_id: driverId, delivery_method: deliveryMethod },
      { headers: { "session-token": sessionToken } },
    );
  },

  /**
   * Get kitchen queue for a restaurant (manager action)
   */
  async getKitchenQueue(restaurantId) {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.get(`/orders/kitchen/${restaurantId}`, {
      headers: { "session-token": sessionToken },
    });
  },

  /**

   * Mark order as cancelled (manager action)
   */
  async cancelOrder(orderId) {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.patch(
      `/orders/${orderId}/status/cancelled`,
      {},
      {
        headers: { "session-token": sessionToken },
      },
    );
  },
};
