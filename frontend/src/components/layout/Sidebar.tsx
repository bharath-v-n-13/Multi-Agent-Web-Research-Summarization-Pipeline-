import React from "react";
import { NavLink } from "react-router-dom";
import { LayoutDashboard, FileText, SearchCode } from "lucide-react";

export const Sidebar: React.FC = () => {
  const menuItems = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "New Research",
      path: "/research",
      icon: SearchCode,
    },
    {
      name: "Research History",
      path: "/reports",
      icon: FileText,
    },
  ];

  return (
    <aside className="w-64 border-r border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-950 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-3.5rem)]">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Navigation
          </p>
          <nav className="mt-2 space-y-1">
            {menuItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                    isActive
                      ? "bg-slate-100 dark:bg-slate-900 text-brand-navy dark:text-slate-100"
                      : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900/50 hover:text-slate-900 dark:hover:text-slate-100"
                  }`
                }
              >
                <item.icon className="h-4 w-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* Sidebar Footer info */}
      <div className="rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/50 p-3">
        <p className="text-[10px] font-semibold text-slate-900 dark:text-slate-300">
          Engine Version
        </p>
        <p className="text-[10px] font-medium text-slate-500 dark:text-slate-400 mt-0.5">
          v1.0.0 (LangGraph-backed)
        </p>
      </div>
    </aside>
  );
};
export default Sidebar;
