import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5173,
    // Docker Desktop on Windows doesn't reliably forward filesystem change
    // events (inotify) across a bind mount into the Linux container, so
    // Vite's default watcher can silently stop picking up edits and keep
    // serving stale transformed modules. Polling works around that at the
    // cost of slightly higher CPU usage while the dev server is idle.
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
  },
});
