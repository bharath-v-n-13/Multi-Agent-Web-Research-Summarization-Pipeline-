import React, { useEffect, useState } from "react";
import { Sun, Moon, ShieldCheck, RefreshCw } from "lucide-react";
import { useTheme } from "../common/ThemeContext";
import axios from "axios";

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  // Ping backend liveness endpoint
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
        const res = await axios.get(`${API_BASE_URL}/health`, { timeout: 3000 });
        if (res.data && res.data.status === "healthy") {
          setIsHealthy(true);
        } else {
          setIsHealthy(false);
        }
      } catch (err) {
        setIsHealthy(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/80 px-6 backdrop-blur-md">
      {/* Branding */}
      <div className="flex items-center space-x-2">
        <svg viewBox="0 0 42 42" className="h-9 w-9" fill="none" xmlns="http://www.w3.org/2000/svg">
          {/* Blue shape */}
          <path
            d="M 12 28 L 19.5 14.5 L 24.5 23.5"
            className="stroke-blue-600 dark:stroke-blue-400"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Red shape */}
          <path
            d="M 21.5 18 L 26.5 27 L 31.5 18"
            className="stroke-red-500 dark:stroke-red-400"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Red ring at bottom left */}
          <circle
            cx="12"
            cy="28"
            r="3"
            className="stroke-red-500 dark:stroke-red-400"
            strokeWidth="2.2"
            fill="none"
          />
          {/* Blue play button circle at top right */}
          <circle
            cx="31.5"
            cy="18"
            r="3.2"
            className="fill-blue-600 dark:fill-blue-400"
          />
          {/* White play triangle */}
          <polygon
            points="30.5,16.5 33.5,18 30.5,19.5"
            fill="white"
          />
        </svg>
        <span className="text-xl font-bold tracking-tight text-blue-600 dark:text-blue-400 font-sans">
          agivant
        </span>
      </div>

      {/* Utilities */}
      <div className="flex items-center space-x-4">
        {/* API Health indicator */}
        <div className="flex items-center space-x-2 rounded-full bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/50 py-1 px-3">
          {isHealthy === null ? (
            <>
              <RefreshCw className="h-3 w-3 animate-spin text-slate-400" />
              <span className="text-[10px] font-medium text-slate-500">Checking API...</span>
            </>
          ) : isHealthy ? (
            <>
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
              <span className="text-[10px] font-medium text-slate-600 dark:text-slate-400">API Connected</span>
            </>
          ) : (
            <>
              <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse" />
              <span className="text-[10px] font-medium text-rose-600 dark:text-rose-400">API Offline</span>
            </>
          )}
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all shadow-sm"
          title={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
          aria-label="Toggle theme"
        >
          {theme === "light" ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4" />
          )}
        </button>
      </div>
    </header>
  );
};
export default Header;
