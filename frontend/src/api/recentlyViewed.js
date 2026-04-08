import api from './axios';

export const recentlyViewedApi = {
  getRecentlyViewed: () =>
    api.get('/recently-viewed'),
};