import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "@/App";
import DashboardPage from "@/features/dashboard";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [{ index: true, element: <DashboardPage /> }],
  },
]);

export function AppRoutes() {
  return <RouterProvider router={router} />;
}
