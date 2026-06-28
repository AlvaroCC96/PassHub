import { useState } from "react";
import { Button } from "@passhub/ui";
import { useAuth } from "@/auth/useAuth";

export function LoginPage() {
  const { loginWithGoogle } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);

  const handleGoogleLogin = async () => {
    setIsRedirecting(true);
    try {
      await loginWithGoogle();
    } catch {
      setIsRedirecting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-semibold">Sign in to PassHub</h1>
      <Button type="button" onClick={handleGoogleLogin} disabled={isRedirecting}>
        {isRedirecting ? "Redirecting…" : "Continue with Google"}
      </Button>
    </div>
  );
}
