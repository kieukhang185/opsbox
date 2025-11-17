import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  base: "/",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        ws: true,
        // keep or drop the /api prefix depending on your API:
        // if your API expects /users (no /api), enable rewrite:
        // rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
});
