import React from "react";

export const Spinner: React.FC<{ size?: "sm" | "md" | "lg"; className?: string }> = ({
  size = "md",
  className = "",
}) => {
  const sizeClasses = {
    sm: "h-5 w-5 border-2",
    md: "h-8 w-8 border-3",
    lg: "h-12 w-12 border-4",
  };

  return (
    <div
      className={`animate-spin rounded-full border-slate-200 border-t-brand-navy dark:border-slate-800 dark:border-t-slate-300 ${sizeClasses[size]} ${className}`}
    />
  );
};

export const PageLoader: React.FC = () => {
  return (
    <div className="flex h-[50vh] w-full flex-col items-center justify-center space-y-4">
      <Spinner size="lg" />
      <p className="text-sm font-medium text-slate-500 animate-pulse">Loading workspace...</p>
    </div>
  );
};

export const CardSkeleton: React.FC<{ count?: number }> = ({ count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, idx) => (
        <div
          key={idx}
          className="w-full rounded-xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-3 animate-pulse shadow-soft"
        >
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/3" />
          <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-full" />
          <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-5/6" />
          <div className="flex justify-between items-center pt-2">
            <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-1/5" />
            <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-1/6" />
          </div>
        </div>
      ))}
    </>
  );
};
