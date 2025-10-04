import { NavLink, Outlet } from "react-router-dom";

function navClass({ isActive }: { isActive: boolean }) {
  const base =
    "block rounded-md px-3 py-2 text-sm font-medium transition-colors";
  const rest = isActive
    ? "bg-zinc-800 text-white"
    : "text-zinc-200 hover:bg-zinc-800 hover:text-white";
  return `${base} ${rest}`;
}

export default function App() {
  return (
    <div className="flex h-screen">
      {/* Sidebar (dark, high contrast) */}
      <aside className="w-64 bg-zinc-900 text-zinc-100 border-r border-zinc-800">
        <div className="p-4 text-xl font-bold tracking-tight">K8s Admin</div>
        <nav className="space-y-1 px-2">
          <NavLink className={navClass} to="/">
            Dashboard
          </NavLink>
          <NavLink className={navClass} to="/namespaces">
            Namespaces
          </NavLink>
          <NavLink className={navClass} to="/nodes">
            Nodes
          </NavLink>
          <NavLink className={navClass} to="/pods">
            Pods
          </NavLink>
          <NavLink className={navClass} to="/events">
            Events
          </NavLink>
        </nav>
      </aside>

      {/* Content */}
      <main className="flex-1 overflow-auto bg-zinc-100 text-zinc-900">
        <header className="sticky top-0 z-10 border-b border-zinc-300 bg-white/90 backdrop-blur px-6 py-3">
          <h1 className="text-lg font-semibold">Kubernetes Dashboard</h1>
        </header>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
