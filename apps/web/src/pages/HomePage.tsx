import { Link } from "react-router-dom";
import { useAuth } from "@/auth/useAuth";

const CTA_CLASSES =
  "inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700";

export function HomePage() {
  const { status } = useAuth();

  return (
    <div className="mx-auto max-w-2xl py-16 text-center">
      <h1 className="text-3xl font-bold">Welcome to PassHub</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">
        One platform for the documentation that matters — vehicles, home, pets, health, and
        family — organized module by module, starting with DrivePass.
      </p>

      {status !== "loading" && (
        <div className="mt-8">
          <Link to={status === "authenticated" ? "/app" : "/login"} className={CTA_CLASSES}>
            {status === "authenticated" ? "Go to Dashboard" : "Sign in to get started"}
          </Link>
        </div>
      )}
    </div>
  );
}
