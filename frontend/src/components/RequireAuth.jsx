import { Navigate } from "react-router-dom";

export default function RequireAuth({ children }) {
  return localStorage.getItem("access_token") ? children : <Navigate to="/login" replace />;
}
