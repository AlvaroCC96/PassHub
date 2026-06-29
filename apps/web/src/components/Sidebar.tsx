import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/app", label: "Dashboard", end: true },
  { to: "/app/drive", label: "DrivePass", end: false },
];

export function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 border-r border-slate-200 p-4 dark:border-slate-800 md:block">
      <nav className="flex flex-col gap-1">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `rounded-md px-3 py-2 text-sm font-medium ${
                isActive
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-600/20 dark:text-brand-400"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
