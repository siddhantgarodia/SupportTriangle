import { Navigate, Outlet } from "react-router-dom";
import { getToken, getUser } from "../auth";

export default function ProtectedRoute({ roles, children }) {
  const token = getToken();
  const user = getUser();

  if (!token || !user) return <Navigate to="/login" replace />;

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/tickets" replace />;
  }

  return children ?? <Outlet />;
}
