import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./components/common/ThemeContext";
import { Toaster } from "sonner";
import MainLayout from "./layouts/MainLayout";

// Lazy load pages for code-splitting and improved bundle size
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const Research = React.lazy(() => import("./pages/Research"));
const Reports = React.lazy(() => import("./pages/Reports"));
const ReportDetails = React.lazy(() => import("./pages/ReportDetails"));

// Setup TanStack Query client with production retry configurations
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes cache stale duration
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <React.Suspense
            fallback={
              <div className="flex h-screen w-screen flex-col items-center justify-center bg-slate-50 dark:bg-slate-950 space-y-4">
                <div className="animate-spin rounded-full border-4 border-slate-200 border-t-brand-navy dark:border-slate-800 dark:border-t-slate-300 h-12 w-12" />
                <span className="text-sm font-semibold tracking-wide text-slate-500 animate-pulse">
                  Initializing portal...
                </span>
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<MainLayout />}>
                <Route index element={<Dashboard />} />
                <Route path="research" element={<Research />} />
                <Route path="reports" element={<Reports />} />
                <Route path="reports/:id" element={<ReportDetails />} />
              </Route>
            </Routes>
          </React.Suspense>
        </BrowserRouter>
        {/* Sonner toast alerts */}
        <Toaster position="top-right" richColors closeButton />
      </ThemeProvider>
    </QueryClientProvider>
  );
};
export default App;
