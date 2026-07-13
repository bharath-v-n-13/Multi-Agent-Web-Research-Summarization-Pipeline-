import React from "react";
import { Outlet } from "react-router-dom";
import Header from "../components/layout/Header";
import Sidebar from "../components/layout/Sidebar";
import Footer from "../components/layout/Footer";

export const MainLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-slate-950 font-sans transition-colors duration-200">
      {/* Main Top Header */}
      <Header />

      {/* Main Body container */}
      <div className="flex flex-1">
        {/* Navigation Sidebar */}
        <Sidebar />

        {/* Dynamic content outlet wrapper */}
        <main className="flex-1 overflow-y-auto px-4 py-6 md:px-8 max-h-[calc(100vh-3.5rem)] flex flex-col justify-between">
          <div className="mx-auto w-full max-w-7xl flex-1 pb-10">
            <Outlet />
          </div>
          
          {/* Main Footer */}
          <Footer />
        </main>
      </div>
    </div>
  );
};
export default MainLayout;
