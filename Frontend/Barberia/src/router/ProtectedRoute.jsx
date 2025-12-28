import { Navigate } from "react-router-dom";
import { useAuthContext } from "../auth/AuthContext";

export default function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuthContext();

  console.log("🟡 ProtectedRoute", {
    loading,
    user,
    roleRequerido: role,
  });

  if (loading) {
    console.log("⏳ loading true, no render");
    return null;
  }

  if (!user) {
    const token = localStorage.getItem("token");
    console.log("🔴 NO USER, token:", token);

    if (token) {
      console.log("⏳ token existe, esperando hidratación");
      return null;
    }

    console.log("➡️ REDIRECT LOGIN (no user)");
    return <Navigate to="/login-barbero" replace />;
  }

  if (role && user.role !== role) {
    console.log(
      "➡️ REDIRECT LOGIN (rol incorrecto)",
      "user.role:",
      user.role,
      "esperado:",
      role
    );
    return <Navigate to="/login-barbero" replace />;
  }

  console.log("🟢 ACCESS GRANTED");
  return children;
}
