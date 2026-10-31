import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The build goes straight into the Python package so `python -m sortify` serves it.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: { outDir: "../sortify/web", emptyOutDir: true },
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
