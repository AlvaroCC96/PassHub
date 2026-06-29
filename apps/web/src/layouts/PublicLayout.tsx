import { Outlet } from "react-router-dom";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";

/** For marketing/public pages — no `Sidebar`, since that's app-shell
 * navigation for an authenticated session and has no business showing up
 * on a page a logged-out visitor can land on. */
export function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1 p-4 md:p-6">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
