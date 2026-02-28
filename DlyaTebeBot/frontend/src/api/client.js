import axios from "axios";

const api = axios.create({
  baseURL: "/api/miniapp/",
});


export default api;