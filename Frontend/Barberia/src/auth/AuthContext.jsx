import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    console.log("🟡 AuthContext INIT");
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    console.log("🟡 localStorage:", { token, role });

    if (token && role) {
      setUser({ token, role });
      console.log("🟢 USER HIDRATADO:", { token, role });
    }

    setLoading(false);
  }, []);

  const login = ({ token, role }) => {
    console.log("🟢 LOGIN CONTEXT:", { token, role });
    localStorage.setItem("token", token);
    localStorage.setItem("role", role);
    setUser({ token, role });
  };

  const logout = () => {
    console.log("🔴 LOGOUT CONTEXT");
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setUser(null);
    navigate("/login-barbero");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => useContext(AuthContext);
