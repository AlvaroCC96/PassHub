export function Footer() {
  return (
    <footer className="border-t border-slate-200 px-4 py-3 text-center text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
      © {new Date().getFullYear()} PassHub. All rights reserved.
    </footer>
  );
}
