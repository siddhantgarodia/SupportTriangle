import { NavLink, useNavigate } from "react-router-dom";
import { getUser, clearAuth } from "../auth";

const navItems = [
  { to: "/tickets", label: "Tickets", roles: ["specialist", "senior", "admin"] },
  { to: "/analytics", label: "Analytics", roles: ["senior", "admin"] },
  { to: "/personas", label: "Personas", roles: ["senior", "admin"] },
  { to: "/users", label: "Users", roles: ["admin"] },
];

export default function Sidebar() {
  const user = getUser();
  const navigate = useNavigate();

  function handleLogout() {
    clearAuth();
    navigate("/login");
  }

  return (
    <aside className="w-56 bg-gray-900 text-white flex flex-col min-h-screen">
      <div className="px-4 py-5 border-b border-gray-700">
        <h1 className="text-lg font-bold">SupportTriangle</h1>
        <p className="text-xs text-gray-400 mt-1 truncate">{user?.email}</p>
        <span className="inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium bg-indigo-600">
          {user?.role}
        </span>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-1">
        {navItems
          .filter((item) => item.roles.includes(user?.role))
          .map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `block px-3 py-2 rounded text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-600 text-white"
                    : "text-gray-300 hover:bg-gray-700 hover:text-white"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
      </nav>
      <div className="px-4 py-4 border-t border-gray-700">
        <button
          onClick={handleLogout}
          className="w-full text-left text-sm text-gray-400 hover:text-white transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
