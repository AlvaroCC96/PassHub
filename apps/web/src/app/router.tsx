import { createBrowserRouter } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthLayout } from "@/layouts/AuthLayout";
import { MainLayout } from "@/layouts/MainLayout";
import { PublicLayout } from "@/layouts/PublicLayout";
import { AuthCallbackPage } from "@/pages/AuthCallbackPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { DrivePassPage } from "@/pages/DrivePassPage";
import { HomePage } from "@/pages/HomePage";
import { LoginPage } from "@/pages/LoginPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { PublicPortalPage } from "@/pages/PublicPortalPage";
import { DocumentDetailPage } from "@/pages/documents/DocumentDetailPage";
import { DocumentsPage } from "@/pages/documents/DocumentsPage";
import { PublicAccessPage } from "@/pages/vehicles/PublicAccessPage";
import { VehicleDetailPage } from "@/pages/vehicles/VehicleDetailPage";
import { VehicleFormPage } from "@/pages/vehicles/VehicleFormPage";
import { VehicleListPage } from "@/pages/vehicles/VehicleListPage";

export const router = createBrowserRouter(
  [
    // ── Public portal (standalone — no Navbar/Footer) ──────────────────────
    { path: "/p/:publicToken", element: <PublicPortalPage /> },

    // ── Marketing pages ────────────────────────────────────────────────────
    {
      element: <PublicLayout />,
      children: [{ path: "/", element: <HomePage /> }],
    },

    // ── Authenticated app shell ────────────────────────────────────────────
    {
      element: <MainLayout />,
      children: [
        {
          element: <ProtectedRoute />,
          children: [
            { path: "/app", element: <DashboardPage /> },
            { path: "/app/drive", element: <DrivePassPage /> },
            { path: "/app/drive/vehicles", element: <VehicleListPage /> },
            { path: "/app/drive/vehicles/new", element: <VehicleFormPage /> },
            { path: "/app/drive/vehicles/:vehicleId", element: <VehicleDetailPage /> },
            { path: "/app/drive/vehicles/:vehicleId/edit", element: <VehicleFormPage /> },
            {
              path: "/app/drive/vehicles/:vehicleId/public-access",
              element: <PublicAccessPage />,
            },
            {
              path: "/app/drive/vehicles/:vehicleId/documents",
              element: <DocumentsPage />,
            },
            {
              path: "/app/drive/vehicles/:vehicleId/documents/:documentId",
              element: <DocumentDetailPage />,
            },
          ],
        },
      ],
    },

    // ── Auth ───────────────────────────────────────────────────────────────
    {
      element: <AuthLayout />,
      children: [
        { path: "/login", element: <LoginPage /> },
        { path: "/auth/callback", element: <AuthCallbackPage /> },
      ],
    },

    { path: "*", element: <NotFoundPage /> },
  ],
  { future: { v7_relativeSplatPath: true } },
);
