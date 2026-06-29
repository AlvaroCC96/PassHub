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
import { VehicleDetailPage } from "@/pages/vehicles/VehicleDetailPage";
import { VehicleFormPage } from "@/pages/vehicles/VehicleFormPage";
import { VehicleListPage } from "@/pages/vehicles/VehicleListPage";

export const router = createBrowserRouter(
  [
    {
      element: <PublicLayout />,
      children: [{ path: "/", element: <HomePage /> }],
    },
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
          ],
        },
      ],
    },
    {
      element: <AuthLayout />,
      children: [
        { path: "/login", element: <LoginPage /> },
        { path: "/auth/callback", element: <AuthCallbackPage /> },
      ],
    },
    { path: "*", element: <NotFoundPage /> },
  ],
  // Opting in early to the v7 behavior react-router currently warns about —
  // no behavior change today, just silences the migration warning.
  // `v7_startTransition` is a `<RouterProvider>` future flag, set in App.tsx.
  { future: { v7_relativeSplatPath: true } },
);
