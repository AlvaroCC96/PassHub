import { ModuleStatus } from "@passhub/shared";
import { Button } from "@passhub/ui";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/useAuth";
import { useCurrentUser } from "@/auth/useCurrentUser";
import { ModuleGrid } from "@/components/ModuleGrid";
import { useEnableModule } from "@/platform/useEnableModule";
import { usePlatformModules } from "@/platform/usePlatformModules";

export function DashboardPage() {
  const { user } = useCurrentUser();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const { modules, isLoading: modulesLoading } = usePlatformModules();
  const enableModule = useEnableModule();
  const [avatarFailed, setAvatarFailed] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  if (!user) return null;

  const enabledModules = modules.filter((m) => m.is_enabled);
  const availableModules = modules.filter((m) => !m.is_enabled && m.status === ModuleStatus.Active);
  const comingSoonModules = modules.filter((m) => m.status === ModuleStatus.ComingSoon);

  return (
    <div className="space-y-10">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {user.avatar_url && !avatarFailed ? (
            <img
              src={user.avatar_url}
              alt={user.full_name ?? user.email}
              referrerPolicy="no-referrer"
              onError={() => setAvatarFailed(true)}
              className="h-12 w-12 rounded-full"
            />
          ) : (
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-200 text-base font-semibold dark:bg-slate-800">
              {(user.full_name ?? user.email).charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-semibold">Welcome back, {user.full_name ?? user.email}</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {user.role} · last login{" "}
              {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "—"}
            </p>
          </div>
        </div>
        <Button variant="secondary" onClick={handleLogout}>
          Log out
        </Button>
      </div>

      {!modulesLoading && (
        <>
          <section>
            <h2 className="text-lg font-semibold">Your modules</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              The PassHub modules enabled on your account.
            </p>
            <div className="mt-4">
              <ModuleGrid modules={enabledModules} />
            </div>
          </section>

          {availableModules.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold">Available modules</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Ready to turn on whenever you need them.
              </p>
              <div className="mt-4">
                <ModuleGrid
                  modules={availableModules}
                  onEnableModule={(module) => enableModule.mutate(module.code)}
                />
              </div>
            </section>
          )}

          <section>
            <h2 className="text-lg font-semibold">Coming soon</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              More modules are on the way for the whole PassHub platform.
            </p>
            <div className="mt-4">
              <ModuleGrid modules={comingSoonModules} />
            </div>
          </section>
        </>
      )}
    </div>
  );
}
