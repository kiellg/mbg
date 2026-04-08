import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const axiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

export const userApi = {
  /**
   * Get all drivers filtered by delivery method
   */
  async getDriversByDeliveryMethod(deliveryMethod) {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.get("/users/drivers", {
      params: { delivery_method: deliveryMethod },
      headers: { "session-token": sessionToken },
    });
  },

  /**
   * Get all drivers
   */
  async getAllDrivers() {
    const sessionToken = localStorage.getItem("session_token");
    return axiosInstance.get("/users/drivers", {
      headers: { "session-token": sessionToken },
    });
  },
};
