import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-950 px-6 py-4 flex flex-col md:flex-row items-center justify-between text-xs text-slate-500 dark:text-slate-500">
      <div>
        <span>© {new Date().getFullYear()} agivant Systems. All rights reserved.</span>
      </div>
      <div className="flex items-center space-x-4 mt-2 md:mt-0">
        <span>Workspace: Desktop/Agent</span>
        <span className="h-3 w-px bg-slate-200 dark:bg-slate-800" />
        <span>OS: Windows Enterprise</span>
      </div>
    </footer>
  );
};
export default Footer;
