import axios from "axios";

const api = axios.create({
  baseURL: "/api/miniapp/",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh");
        const res = await axios.post("/api/token/refresh/", {
          refresh: refreshToken,
        });
        localStorage.setItem("access", res.data.access);
        api.defaults.headers.common["Authorization"] = `Bearer ${res.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("telegram_id");
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;