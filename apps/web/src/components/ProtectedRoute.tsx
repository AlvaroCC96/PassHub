import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/auth/useAuth";
import { Loading } from "@/components/Loading";

export function ProtectedRoute() {
  const { status } = useAuth();

  if (status === "loading") return <Loading />;
  if (status === "unauthenticated") return <Navigate to="/login" replace />;
  return <Outlet />;
}
