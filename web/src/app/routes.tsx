import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "@/App";
import DashboardPage from "@/features/dashboard";
import NamespacesPage from "@/features/namespaces";
import EventsPage from "@/features/events";
import NodesPage from "@/features/nodes";
import PodsPage from "@/features/pods";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "namespaces", element: <NamespacesPage /> },
      { path: "nodes", element: <NodesPage /> },
      { path: "pods", element: <PodsPage /> },
      { path: "events", element: <EventsPage /> },
    ],
  },
]);

export function AppRoutes() {
  return <RouterProvider router={router} />;
}
