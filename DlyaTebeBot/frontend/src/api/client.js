import axios from "axios";

const BACKEND = "http://localhost:8000";

const api = axios.create({
  baseURL: "/api/miniapp",
});

export default api;
