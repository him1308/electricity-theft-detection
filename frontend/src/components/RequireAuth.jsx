import { Navigate } from "react-router-dom";

export default function RequireAuth({ children, roles }) {
  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.map((item) => item.toLowerCase()).includes((role || "").toLowerCase())) {
    return <Navigate to="/" replace />;
  }

  return children;
}
