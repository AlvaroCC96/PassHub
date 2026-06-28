import { Button } from "@passhub/ui";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/useAuth";
import { useCurrentUser } from "@/auth/useCurrentUser";

export function DashboardPage() {
  const { user } = useCurrentUser();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [avatarFailed, setAvatarFailed] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  if (!user) return null;

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <Button variant="secondary" onClick={handleLogout}>
          Log out
        </Button>
      </div>

      <div className="mt-6 flex items-center gap-4">
        {user.avatar_url && !avatarFailed ? (
          <img
            src={user.avatar_url}
            alt={user.full_name ?? user.email}
            referrerPolicy="no-referrer"
            onError={() => setAvatarFailed(true)}
            className="h-16 w-16 rounded-full"
          />
        ) : (
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-200 text-lg font-semibold dark:bg-slate-800">
            {(user.full_name ?? user.email).charAt(0).toUpperCase()}
          </div>
        )}
        <div>
          <p className="text-lg font-medium">{user.full_name ?? "—"}</p>
          <p className="text-sm text-slate-600 dark:text-slate-400">{user.email}</p>
        </div>
      </div>

      <dl className="mt-6 grid grid-cols-2 gap-4 text-sm sm:max-w-md">
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Role</dt>
          <dd className="font-medium capitalize">{user.role}</dd>
        </div>
        <div>
          <dt className="text-slate-500 dark:text-slate-400">Last login</dt>
          <dd className="font-medium">
            {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "—"}
          </dd>
        </div>
      </dl>
    </div>
  );
}
