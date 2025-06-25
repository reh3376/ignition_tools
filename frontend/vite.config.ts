import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Allow external connections
    hmr: {
      overlay: true, // Show errors as overlay
    },
    watch: {
      usePolling: true, // Use polling for file watching (helps with some systems)
      interval: 100, // Check for changes every 100ms
    },
  },
  build: {
    sourcemap: true, // Enable source maps for debugging
  },
  optimizeDeps: {
    include: ["react", "react-dom"], // Pre-bundle these dependencies
  },
});
