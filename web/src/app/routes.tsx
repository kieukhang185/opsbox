import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "@/App";
import DashboardPage from "@/features/dashboard";
import EventsPage from "@/features/events";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "events", element: <EventsPage /> },
    ],
  },
]);

export function AppRoutes() {
  return <RouterProvider router={router} />;
}
