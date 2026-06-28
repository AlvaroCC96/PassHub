import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/useAuth";
import { Loading } from "@/components/Loading";

/** Lands here after Google redirects back through `GET /api/v1/auth/callback`.
 * The backend already set the refresh-token cookie at that point — no tokens
 * ever appear in this page's URL. All that's left is to mint an access token
 * from the cookie and move on to the dashboard. */
export function AuthCallbackPage() {
  const { restoreSession } = useAuth();
  const navigate = useNavigate();
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    void restoreSession().then((success) => {
      navigate(success ? "/dashboard" : "/login", { replace: true });
    });
  }, [restoreSession, navigate]);

  return <Loading />;
}
