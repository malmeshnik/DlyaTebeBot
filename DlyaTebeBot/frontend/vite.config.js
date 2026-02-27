import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/miniapp/",
  plugins: [react()],
  // На проді забрати проксування на локалхост. Там працює nginx
  server: {
    port: 5173,
    allowedHosts: [
      "bb6d-91-229-122-68.ngrok-free.app"
    ],
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/media": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});