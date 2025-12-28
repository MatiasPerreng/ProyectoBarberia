import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // =========================
  // INIT – recuperar sesión
  // =========================
  useEffect(() => {
    console.log("🟡 AuthContext INIT");

    const token = localStorage.getItem("token");

    if (token) {
      try {
        const payload = jwtDecode(token);

        setUser({
          token,
          role: payload.role,
          nombre: payload.nombre,
          apellido: payload.apellido,
          id: payload.sub,
        });
      } catch (err) {
        console.error("❌ Token inválido", err);
        localStorage.removeItem("token");
        setUser(null);
      }
    }

    setLoading(false);
  }, []);

  // =========================
  // LOGIN
  // =========================
  const login = ({ token }) => {
    const payload = jwtDecode(token);

    localStorage.setItem("token", token);

    setUser({
      token,
      role: payload.role,
      nombre: payload.nombre,
      apellido: payload.apellido,
      id: payload.sub,
    });
  };

  // =========================
  // LOGOUT
  // =========================
  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    navigate("/login-barbero");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        loading,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => useContext(AuthContext);
