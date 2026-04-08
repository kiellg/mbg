import api from "./axios";

export const restaurantApi = {
  // Browse
  getAll: () => api.get("/restaurants"),
  getAllPaginated: (page = 1, limit = 10, sort_by = "rating", order = "desc") =>
    api.get("/restaurants/paginated/sorted", {
      params: { page, limit, sort_by, order },
    }),
  getSorted: (sort_by = "rating", order = "desc") =>
    api.get("/restaurant/sorted", { params: { sort_by, order } }),

  // Restaurant detail + menu
  getMenu: (restaurantId) => api.get(`/restaurants/${restaurantId}/menu`),
  getMenuPaginated: (restaurantId, page = 1, limit = 10) =>
    api.get(`/restaurants/${restaurantId}/menu/paginated`, {
      params: { page, limit },
    }),
  getMenuPaginatedSorted: (
    restaurantId,
    page = 1,
    limit = 10,
    sort_by = "price",
    order = "asc",
  ) =>
    api.get(`/restaurants/${restaurantId}/menu/paginated/sorted`, {
      params: { page, limit, sort_by, order },
    }),

  // Menu items
  getMenuItem: (restaurantId, itemId) =>
    api.get(`/restaurants/${restaurantId}/menu/${itemId}`),

    // Search & filter
    search: (q) =>
        api.get('/restaurants/search', { params: { q } }),
    searchMenuItems: (q) =>
        api.get('/restaurants/menu/search', { params: { q } }),
    getSuggestions: (q) =>
        api.get('/restaurants/search/suggestions', { params: { q } }),
    filter: (cuisine_types) => {
        const params = new URLSearchParams();
        cuisine_types.forEach(t => params.append('cuisine_types', t));
        return api.get(`/restaurants/filter?${params.toString()}`);
    },
    getCategories: () =>
        api.get('/restaurants/categories'),

  // CRUD (manager)
  create: (payload) => {
    const sessionToken = localStorage.getItem("session_token");
    return api.post("/restaurants", payload, {
      headers: { "session-token": sessionToken },
    });
  },
  update: (restaurantId, payload) => {
    const sessionToken = localStorage.getItem("session_token");
    return api.patch(`/restaurants/${restaurantId}`, payload, {
      headers: { "session-token": sessionToken },
    });
  },
  delete: (restaurantId) => {
    const sessionToken = localStorage.getItem("session_token");
    return api.delete(`/restaurants/${restaurantId}`, {
      headers: { "session-token": sessionToken },
    });
  },
  createMenuItem: (restaurantId, payload) => {
    const sessionToken = localStorage.getItem("session_token");
    return api.post(`/restaurants/${restaurantId}/menu`, payload, {
      headers: { "session-token": sessionToken },
    });
  },
  updateMenuItem: (restaurantId, itemId, payload) => {
    const sessionToken = localStorage.getItem("session_token");
    return api.patch(`/restaurants/${restaurantId}/menu/${itemId}`, payload, {
      headers: { "session-token": sessionToken },
    });
  },
  deleteMenuItem: (restaurantId, itemId) => {
    const sessionToken = localStorage.getItem("session_token");
    return api.delete(`/restaurants/${restaurantId}/menu/${itemId}`, {
      headers: { "session-token": sessionToken },
    });
  },
};
