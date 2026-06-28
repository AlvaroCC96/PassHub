import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-2 py-16 text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-slate-600 dark:text-slate-400">This page does not exist.</p>
      <Link to="/" className="text-brand-600 hover:underline dark:text-brand-400">
        Back home
      </Link>
    </div>
  );
}
