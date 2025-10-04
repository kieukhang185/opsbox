import { NavLink, Outlet } from "react-router-dom";

export default function App() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-white">
        <div className="p-4 font-bold text-xl">K8s Admin</div>
        <nav className="space-y-1 px-2">
          <NavLink
            className="block rounded px-3 py-2 hover:bg-slate-100"
            to="/"
          >
            Dashboard
          </NavLink>
          <NavLink
            className="block rounded px-3 py-2 hover:bg-slate-100"
            to="/events"
          >
            Events
          </NavLink>
        </nav>
      </aside>
      {/* Content */}
      <main className="flex-1 overflow-auto bg-slate-50">
        <header className="sticky top-0 z-10 border-b bg-white px-6 py-3">
          <h1 className="text-lg font-semibold">Kubernetes Dashboard</h1>
        </header>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
