import { AlertTriangle, BarChart3, Gauge, LayoutDashboard, LogOut, Upload, Users, Zap } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { logout } from "../services/api";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/consumers", label: "Consumers", icon: Users },
  { to: "/alerts", label: "Alerts", icon: AlertTriangle },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/model", label: "Model", icon: Gauge },
  { to: "/upload", label: "Upload", icon: Upload }
];

export default function Layout() {
  const navigate = useNavigate();
  const role = localStorage.getItem("role") || "Analyst";

  function signOut() {
    logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-grid-surface text-slate-900">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-grid-line bg-white lg:block">
        <div className="flex h-20 items-center gap-3 border-b border-grid-line px-6">
          <div className="grid h-11 w-11 place-items-center rounded-lg bg-grid-ink text-white">
            <Zap size={22} />
          </div>
          <div>
            <p className="text-lg font-bold text-grid-ink">GridGuard</p>
            <p className="text-xs font-medium uppercase tracking-wide text-grid-teal">Energy Analytics</p>
          </div>
        </div>
        <nav className="space-y-1 p-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-semibold transition ${
                  isActive ? "bg-grid-ink text-white" : "text-slate-600 hover:bg-slate-100 hover:text-grid-ink"
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 flex h-20 items-center justify-between border-b border-grid-line bg-white/95 px-5 backdrop-blur lg:px-8">
          <div>
            <p className="text-sm font-medium text-slate-500">Power Distribution Control Center</p>
            <h1 className="text-xl font-semibold text-grid-ink">Suspicious Consumption Monitoring</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">{role}</span>
            <button onClick={signOut} className="rounded-md border border-grid-line bg-white p-2.5 text-slate-600 hover:text-grid-ink" title="Sign out">
              <LogOut size={18} />
            </button>
          </div>
        </header>
        <main className="p-5 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
