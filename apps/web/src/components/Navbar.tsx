import { Link } from "react-router-dom";
import { useTheme } from "@/theme/ThemeProvider";

export function Navbar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
      <Link to="/" className="text-lg font-semibold">
        PassHub
      </Link>
      <button
        type="button"
        onClick={toggleTheme}
        aria-label="Toggle dark mode"
        className="rounded-md px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        {theme === "dark" ? "Light mode" : "Dark mode"}
      </button>
    </header>
  );
}
