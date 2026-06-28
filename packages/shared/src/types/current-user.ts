import type { AuthProvider } from "./auth-provider";
import type { Role } from "./role";

/** Mirrors `CurrentUserResponse` returned by `GET /api/v1/auth/me`. */
export interface CurrentUser {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: Role;
  provider: AuthProvider;
  last_login_at: string | null;
}
